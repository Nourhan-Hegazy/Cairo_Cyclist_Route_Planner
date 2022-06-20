from flask import Flask, request
import flask
import json 
from flask_cors import CORS
import requests
from urllib.parse import urlencode
import networkx as nx
from enum import unique
import math
import osmnx as ox
from shapely.geometry import Point,Polygon
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gp
import pandas as pd
import csv
from pyproj import Proj
from math import hypot
import pyproj
from shapely.geometry import shape
from shapely.ops import transform
import time
import googlemaps
import requests
from urllib.parse import urlencode
from os.path import exists
from requests import get,post
app = Flask(__name__)
CORS(app)
ox.config(use_cache=True, log_console=True)
def get_weather():
 url=f"http://api.openweathermap.org/data/2.5/air_pollution?lat=30.049999&lon=31.65&appid=d0715f9fcb74eba73da5d00ececdc6fb"
 url1=f'https://api.openweathermap.org/data/2.5/onecall?lat=30.049999&lon=31.65&units=metric&exclude=hourly,daily&appid=d0715f9fcb74eba73da5d00ececdc6fb'
 r = requests.get(url1)
 x=requests.get(url)
 if (r.status_code not in range(200, 299)): 
   return {}
 elif(x.status_code not in range(200, 299)):
     return {}
 weather={}
 try:
    
    uvi=r.json()['current']['uvi']
    visibility=r.json()['current']['visibility']
    wind_speed=r.json()['current']['wind_speed']
    aqi=x.json()['list'][0]['main']['aqi']
    weather={'uvi':uvi,'visibility':visibility,'wind_speed':wind_speed*2.237,'aqi':aqi}
 except:
        pass
 return weather
def createNetwork(loc,des):
 print(loc)
 print(des)

 (lon1,lat1)=loc
 (lon2,lat2)=des
 p = Proj(proj='utm',zone=36,ellps='WGS84', preserve_units=False)
 x1,y1 = p(lon1,lat1)#lon,lat 30.0729° N, 31.3458° E  30.0186° N, 31.5015° E /30.0329° N, 31.4100° E Latitude: 30.0664361543. Longitude: 31.3497284294 ...

 x2,y2=p(lon2, lat2)#29.9868° N, 31.4413° E

# print(p(x1,y1,inverse=True))
# print((x1,y1))
# print((x2,y2))
 distance_limit =2000 # 10000
 lon1,lat1=p(x1+distance_limit,y1-distance_limit,inverse=True)
 lon2,lat2=p(x1+distance_limit,y2+distance_limit,inverse=True)
 lon3,lat3=p(x2-distance_limit,y1-distance_limit,inverse=True)
 lon4,lat4=p(x2-distance_limit,y2+distance_limit,inverse=True)
 p1=[lon1,lat1]
 p2=[lon2,lat2]
 p3=[lon3,lat3]
 p4=[lon4,lat4]
# coords = [(24.950899, 60.169158), (24.953492, 60.169158), (24.953510, 60.170104), (24.950958, 60.169990)] 
 area=Polygon([p1,p2,p4,p3])
 G = ox.graph.graph_from_polygon(area, network_type='all')
 return G
def possible_paths(G,loc,des):
 (lon1,lat1)=loc
 (lon2,lat2)=des
#  edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
#  nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
#  print(edges[edges.osmid==645457735])
#  print(edges.loc[(29542602,7208831013 ,0  )]['geometry'])
#  print(G.edges[(29542602,7208831013 ,0  )]['length'])
#  print(G.edges[250642077])
 loc=ox.distance.nearest_nodes(G,lon1,lat1 ,return_dist=False)
 des=ox.distance.nearest_nodes(G, lon2, lat2, return_dist=False)
#  print((G.nodes[loc]['x'],G.nodes[loc]['y']))
 l=ox.distance.k_shortest_paths(G, loc, des,50, weight='length')
#  i=0
 x=[]
#  print(type(l))
 for p in l:
  # i=i+1
#   print(len(p))
  x.append(p)
#  print (G.nodes[x[0][0]]["x"])
#  print (G.nodes[x[0][0]]["y"])
 
 return x
def polygon_to_utm(poly):
  s = shape(poly)
  wgs84 = pyproj.CRS('EPSG:4326')
  utm = pyproj.CRS('EPSG:32636')
  project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
  project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform

  return(transform(project, s))
def getParks(loc,des):
  (lon1,lat1)=loc
  (lon2,lat2)=des
  tags={'landuse':['garden','greenfield','grass','park'],'leisure': ['garden','greenfield','grass','park'],'amenity':['park','garden']}
  p = Proj(proj='utm',zone=36,ellps='WGS84', preserve_units=False)
  x1,y1 = p(lon1,lat1)#lon,lat 30.0186° N, 31.5015° E 30.0329° N, 31.4100° E

  x2,y2=p(lon2, lat2)#29.9868° N, 31.4413° E

  # lon1,lat1=p(x1+10000,y1-10000,inverse=True)
  # lon2,lat2=p(x1+10000,y2+10000,inverse=True)
  # lon3,lat3=p(x2-10000,y1-100000,inverse=True)
  # lon4,lat4=p(x2-10000,y2+10000,inverse=True)

  distance_limit = 2000 # 10000
  lon1,lat1=p(x1+distance_limit,y1-distance_limit,inverse=True)
  lon2,lat2=p(x1+distance_limit,y2+distance_limit,inverse=True)
  lon3,lat3=p(x2-distance_limit,y1-distance_limit,inverse=True)
  lon4,lat4=p(x2-distance_limit,y2+distance_limit,inverse=True)
  p1=[lon1,lat1]
  p2=[lon2,lat2]
  p3=[lon3,lat3]
  p4=[lon4,lat4]
# coords = [(24.950899, 60.169158), (24.953492, 60.169158), (24.953510, 60.170104), (24.950958, 60.169990)] 
  area=Polygon([p1,p2,p4,p3])
  parks =ox.geometries.geometries_from_polygon(area, tags)
  p=[]

  for i in range(0,len(parks)):
    pol=parks['geometry'][i]

    p.append(polygon_to_utm(pol))
  return p
def getIndustrial(loc,des):
  # tags = {'natural':'wood','natural':'tree_row',"natural":'tree'}
  tags={'landuse':['industrial']}
  (slon1,slat1)=loc
  (slon2,slat2)=des
  p = Proj(proj='utm',zone=36,ellps='WGS84', preserve_units=False)
  x1,y1 = p(slon1,slat1)#lon,lat 30.0186° N, 31.5015° E

  x2,y2=p(slon2, slat2)#29.9868° N, 31.4413° E
  minx=min(x1,x2)
  miny=(min(y1,y2))
  maxx=max(x1,x2)
  maxy=max(y1,y2)

  distance_limit = 2000 # 10000
  lon1,lat1=p(minx+distance_limit,miny-distance_limit,inverse=True)
  lon2,lat2=p(minx+distance_limit,maxy+distance_limit,inverse=True)
  lon3,lat3=p(maxx-distance_limit,miny-distance_limit,inverse=True)
  lon4,lat4=p(maxx-distance_limit,maxy+distance_limit,inverse=True)

  # lon1,lat1=p(minx-10000,miny-10000,inverse=True)
  # lon2,lat2=p(minx-10000,maxy+100000,inverse=True)
  # lon3,lat3=p(maxx+10000,miny-100000,inverse=True)
  # lon4,lat4=p(maxx+10000,maxy+10000,inverse=True)
  p1=[lon1,lat1]
  p2=[lon2,lat2]
  p3=[lon3,lat3]
  p4=[lon4,lat4]
# coords = [(24.950899, 60.169158), (24.953492, 60.169158), (24.953510, 60.170104), (24.950958, 60.169990)] 
  area=Polygon([p1,p2,p4,p3])
  parks =ox.geometries.geometries_from_polygon(area, tags)

  p=[]
  
  for i in range(0,len(parks)):
    pol=parks['geometry'][i]

    p.append(polygon_to_utm(pol))
  return p
def get_traffic_delay(slon,slat,dlon,dlat):
    endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {"origins": slat+","+slon,"destinations":dlat+","+dlon,"departure_time":"now","key":'AIzaSyDtSGH4mC675HIpzM6o_JIvb8SNhv6c1Fs'}
    url_params = urlencode(params)
    url = f"{endpoint}?{url_params}"
    r = requests.get(url)
    duration=int(r.json()["rows"][0]["elements"][0]["duration"]["text"].split()[0])
    duration_in_traffic=int(r.json()["rows"][0]["elements"][0]["duration_in_traffic"]["text"].split()[0])
    if(duration_in_traffic<duration):
      duration_in_traffic=duration
    return duration_in_traffic-duration
def getElevations(x):
  (lon,lat)=x[0]
  s=str(lat)+","+str(lon)
  for i in range (1,len(x)):
      (lon,lat)=x[i]
      s=s+"|"+str(lat)+","+str(lon)
  
  endpoint = f"https://maps.googleapis.com/maps/api/elevation/json"
  params = {"locations":s, "key":'AIzaSyDtSGH4mC675HIpzM6o_JIvb8SNhv6c1Fs'}
  url_params = urlencode(params)
  url = f"{endpoint}?{url_params}"
  r = requests.get(url)
  if r.status_code not in range(200, 299): 
    return {}
  results=[]
  try:
       for i in range(0,len(r.json()['results'])):
         results.append(r.json()['results'][i]['elevation'])
  except:
          pass
  return results
def osmid_lonlat(graph,osmid):
  lon=graph.nodes[osmid]['x']
  lat=graph.nodes[osmid]['y']
  return(lon,lat)
###########
def route(loc,des):
#  loc=( 31.3473,30.0619)#° N, 31.3458° E 30.0203° N, 31.4950° E 30.0329° N, 31.4100° E
#  des=(31.3458,30.0729) 
 graph=createNetwork(loc,des)
 paths=possible_paths(graph,loc,des)
#  ox.plot.plot_graph_routes(graph, paths, route_colors=['r','y','g','b','r'], route_linewidths=[1,20,14,5,10])
 
#  plt.show()
 industries=getIndustrial(loc,des)
 
 
 street_type=[]
 ed=[] #edges geometry
 lengths=[] #edges lengths
 edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
 
 #############paths network#########################
 poi = nx.DiGraph()#network containing all edges of interest
 parks=getParks(loc,des)#green areas geometries in utm in the bounding box 
 
 for streets in paths:#assigning edge attributes geometry,length,highway,u(loc in lon,lat),v(des in lon,lat)
     for i in range(0,len(streets)-1):
      e=edges.loc[(streets[i],streets[i+1],0  )]['geometry']
      l=edges.loc[(streets[i],streets[i+1],0  )]['length']
      s=edges.loc[(streets[i],streets[i+1],0  )]['highway']
      if(isinstance(s,list)):
       s=s[0]
      poi.add_edge(streets[i],streets[i+1])
      poi[streets[i]][streets[i+1]]['geometry']=polygon_to_utm(e)#line in utm coordinates
      poi[streets[i]][streets[i+1]]['length']=l
      poi[streets[i]][streets[i+1]]['highway']=s
      poi[streets[i]][streets[i+1]]['u']=(graph.nodes[streets[i]]['x'],graph.nodes[streets[i]]['y'])
      poi[streets[i]][streets[i+1]]['v']=(graph.nodes[streets[i+1]]['x'],graph.nodes[streets[i+1]]['y'])
      print( poi[streets[i]][streets[i+1]]['u'])
      print( poi[streets[i]][streets[i+1]]['v'])
      print('---------------')
      ####elev of nodes###
     print('############################')
 osmid=list(poi.nodes)#osmids of all nodes in the network

 
 nodes=[]#lon/lat of all nodes in network
 for o in osmid:
    osmid_lonlat(graph,o) 
    nodes.append(osmid_lonlat(graph,o))
    el=getElevations(nodes)
    ####
 q=ox.stats.count_streets_per_node(graph, nodes=list(poi.nodes))#nodes # of intersecting streets
#####to get average length of edges####
 len1=0
 for u,v,a in poi.edges(data=True):
   len1=len1+poi.edges[(u,v)]['length']
 avg_length=len1/len(poi.edges)
 ###############uv_cost/edge#####
 tx=[]
 for u,v,a in poi.edges(data=True):
     c=0
     shed=0#total area of green areas in 100m buffer of an edge
     line=poi.edges[(u,v)]['geometry']
     buffer=line.buffer(100)#uv buffer analysis
     b2=line.buffer(500)#poll buffer analysis
     green_500=0
     bf=buffer###
     for park in parks:
       
       if(buffer.intersects(park)):
         shed=shed+buffer.intersection(park).area
         bf=bf.difference(buffer.intersection(park))###
       if(b2.intersects(park)):
         green_500= green_500+b2.intersection(park).area
     print(shed/buffer.area)
     # ax = plt.gca()
     # ax.set_facecolor('k')
     # p = gp.GeoSeries(bf)
     # p=p.plot()
     # p.set_facecolor('g')
     # plt.show()
     # plt.plot(*bf.exterior.xy)#
     # plt.show()#
     tx.append(shed/buffer.area)
     shadow=poi[u][v]['shadow']=shed/buffer.area
     poi[u][v]['green_500']=green_500/b2.area
     if(0.01<=shadow<0.05):
       poi[u][v]['shadow']=0.8
     elif(0.05<=shadow<0.1):
       poi[u][v]['shadow']=0.6
     elif(0.1<=shadow<0.15):
       poi[u][v]['shadow']=0.4
     elif(0.15<=shadow<0.2):
       poi[u][v]['shadow']=0.2
     elif(0.2<=shadow):
       poi[u][v]['shadow']=0
     else:
       poi[u][v]['shadow']=1
     
     poi[u][v]['uv_cost']=poi.edges[(u,v)]['shadow']*poi.edges[(u,v)]['length']
 ############Air_pollution/edge (1)###############

     shadow=poi.edges[(u,v)]['green_500']#percentage of green areas in 500m buffer
     #every class of the following removes extra 0.5 min(5% extra pollution) from traffic
     (slon,slat)= a['u']
     (dlon,dlat)= a['v']
     traffic=get_traffic_delay(str(slon),str(slat),str(dlon),str(dlat))
     traffic=traffic/10#1min=10%extra meters of pollution
 
     time.sleep(0.5)
     if(0.01<=shadow<0.05):
       green=0.05
     elif(0.05<=shadow<0.1):
       green=0.1
     elif(0.1<=shadow<0.15):
       green=0.15
     elif(0.15<=shadow<0.2):
       green=0.2
     elif(0.2<=shadow<0.25):
       green=0.25
     elif(0.25<=shadow<0.3):
       green=0.3
     elif(0.3<=shadow<0.35):
       green=0.35
     elif(0.35<=shadow<0.4):
       green=0.4
     else:
       green=0
     poi[u][v]['traffic']=traffic
     poi[u][v]['green']=green
 
     poi[u][v]['pollution_meter']=(1+traffic-green)*poi.edges[(u,v)]['length']
 ##############Elevations##############

  ####elevation_cost/edge####
 
     y1= osmid.index(u)#getting the index of loc to map it to  its elevation
     y2=osmid.index(v)#getting the index of des to map it to  its elevation
     y=el[y2]-el[y1]
     x=poi.edges[(u,v)]['length']
     r=0
     slope=y/x
     poi[u][v]['gradient']=slope
     if(slope<0.01):
      r=0
     elif (0.01<=slope<0.03):
        r=0.2
     elif(0.03<=slope<0.06):
        r=0.6
     elif(slope>=0.06):
        r=1
     poi[u][v]['elevation_cost']=r*poi.edges[(u,v)]['length']
     print (poi.edges[(u,v)]['elevation_cost'])
     print (poi.edges[(u,v)]['shadow'])
   
  ############Air_pollution/edge (2)###############
  #for every level of elevation the consumption of pollution increase
 
     grade=poi.edges[(u,v)]['gradient']
     con=1
     if(0.01<=grade<0.03):
      con=0.6
     elif(0.03<=grade<0.06):
      con=0.8
     elif(grade>=0.06):
      con=1
     elif(0<=grade<0.01):
      con=0.5
     elif(-0.03<=grade<0):
      con=0.4
     elif(-0.06<=grade<-0.03):
      con=0.2
     elif(grade<-0.06):
      con=0
     poi[u][v]['poll_cost']= poi.edges[(u,v)]['pollution_meter']*con
 
  #############intersections#########
 
 
 #####to get average length of edges####
 

 
  
     count=q[v]
     if(count>3):
       r=1
       c=c+1
     else:
        r=0
     poi[u][v]['intersection']=r
     poi[u][v]['intersection_cost']=r*avg_length
    # print(r)
   ############weights############
 weather=get_weather()
 print("!!!!!!!!!!!!!!!the weather now is:")
 print(weather)
 ww=0
 if(2<weather['uvi']<=5):
   ww=1
 elif(5<weather['uvi']<=7):
   ww=100
 elif(7<weather['uvi']):
   ww=1000
 wp=0
 if(weather['aqi']==2):
   wp=1
 elif(weather['aqi']==3):
   wp=100
 elif(weather['aqi']>3):
   wp=1000
 wi=1
 if(500<weather['visibility']<=2000):
   wi=100
 elif(weather['visibility']<500):
   wi=1000
 we=1
 if(15<=weather['wind_speed']<20):
   we=100
 if(weather['wind_speed']>=20):
   we=1000
 
 #########path_cost###########
 (lon1,lat1)=loc
 (lon2,lat2)=des
 loc=ox.distance.nearest_nodes(graph,lon1,lat1 ,return_dist=False)
 des=ox.distance.nearest_nodes(graph, lon2, lat2, return_dist=False)
 paths=list(nx.all_simple_edge_paths(poi, loc,des, cutoff=None))
 # pos = nx.spring_layout(poi)
 
 c=0
 paths_costs=[]
 uv_costs=[]
 el_costs=[]
 int_costs=[]
 poll_costs=[]
 lens=[]
 ints=[]
 costs=[]
 gains=[]
 for p in paths:
  uv_cost=0
  el_cost=0
  int_cost=0
  poll_cost=0
  lent=0
  gain=0
  intr=0
  for ed in p:
    (u,v)=ed
    a=poi.get_edge_data(u, v, default=None)#
   #  print(poi.edges[(u,v)]['intersection_cost'])
    print(poi.edges[(u,v)]['u'])
    print(poi.edges[(u,v)]['v'])
    print('**********')
   
    uv_cost=uv_cost+poi.edges[(u,v)]['uv_cost']
    el_cost=el_cost+poi.edges[(u,v)]['elevation_cost']
    int_cost=int_cost+poi.edges[(u,v)]['intersection_cost']
    poll_cost=poll_cost+poi.edges[(u,v)]['poll_cost']
    lent=lent+poi.edges[(u,v)]['length']
    intr=intr+poi.edges[(u,v)]['intersection']
    if(poi.edges[(u,v)]['gradient']>0):
     gain=gain+poi.edges[(u,v)]['gradient']
  uv_costs.append(uv_cost)
  el_costs.append(el_cost)
  print(p)
  print(poll_costs)
  print(lens)
  gains.append(gain)
  int_costs.append(int_cost)
  ints.append(intr)
  lens.append(lent)
  poll_costs.append(poll_cost)
  costs.append(uv_cost)
  costs.append(el_cost)
  path_cost={"uv_cost":uv_cost,"elevation_cost":el_cost,'length':lent,'intersection_cost':int_cost,'poll_cost':poll_cost}
 
  paths_costs.append(path_cost) 
  print('###################')
  print (path_cost)
  print(intr)
  print('###################*********')
 maxi=max(costs)
 gainMax=max(gains)
 max_uv=max(uv_costs)
 max_el=max(el_costs)
 max_int=max(int_costs)
 max_pol=max(poll_costs)
 
 ################????
 # for p in paths_costs:
 #   p['uv_cost']= (p['uv_cost']-min(uv_costs))/(max(uv_costs)-min(uv_costs))
 #   p['elevation_cost']= (p['elevation_cost']-min(el_costs))/(max(el_costs)-min(el_costs))
 #   p['intersection_cost']= (p['intersection_cost']-min(int_costs))/(max(int_costs)-min(int_costs))
 #   p['poll_cost']= (p['poll_cost']-min(poll_costs))/(max(poll_costs)-min(poll_costs))
 #############normalization#############^^^^^^
 c=0
 paths_costs_n=[]
 normalized_cost=0
 m=[]
 for p in paths_costs:
    normalized_cost=0
    uv_cost=int(p['uv_cost'])
    int_cost=int(p['intersection_cost'])
    el_cost=int(p['elevation_cost'])
    poll_cost=int(p['poll_cost'])
    lent=p['length']
    
    normalized_cost=ww*uv_cost+we*el_cost+wi*int_cost+wp*poll_cost
    paths_costs_n.append(normalized_cost)
    print("weightsssssssssssss")
    print([ww,we,wi,wp])
 # print(paths_costs) 
 best=paths[paths_costs_n.index(min(paths_costs_n))]
 green_route=[]
 i=0
 points=[]
 all_paths=[]
 for path in paths:
     points=[]
     i=0
     for way in path:
         (x,y)=way
         points.append(nodes[osmid.index(x)])
         if(i==len(best)-1):
           points.append(nodes[osmid.index(y)])
         i=i+1
     all_paths.append(points)
 green_route=all_paths[paths_costs_n.index(min(paths_costs_n))]   

#  green_route=all_paths[poll_costs.index(min(poll_costs))]   
#  green_route=all_paths[2]   
 i=0
 unique=[]
 unique.append(green_route[0])
 for po in green_route:
  for pathx in all_paths:
   try:
       ind=pathx.index(po)
   except ValueError:
        unique.append(po)
 unique.append(green_route[len(green_route)-1])
 print (green_route)
#  for way in best:
#      (x,y)=way
#      green_route.append(nodes[osmid.index(x)])
#      if(i==len(best)-1):
#       
#    green_route.append(nodes[osmid.index(y)])
 route=[]
 best=paths[1]
 for p in best:
   (x,y)=way=p
   route.append(x)
   if(i==len(best)-1):
    route.append(y)
 #  green_route=all_paths[poll_costs.index(min(poll_costs))]   
 #  green_route=all_paths[2]   
 map= ox.folium.plot_route_folium(graph, route, route_map=None, popup_attribute=None, tiles='OpenStreetMap', zoom=1, fit_bounds=True)
 map.save('index.html')
     
#      i=i+1
 
    
 return(green_route)
 # print(min(int_costs))
 # print(int_costs[paths_costs_n.index(min(paths_costs_n))])
 # print(lens.index(min(lens)))
 
 # print(ints)
 # print(gains)
 # print(el_costs)
 # print(uv_costs)
 # print(poll_costs)
 # print(gains.index(min(gains)))
 # print(el_costs.index(min(el_costs)))
 # print(min(el_costs))
 # print(el_costs[12])
 # print(gains[el_costs.index(min(el_costs))])
 # print(min(gains))
 # print(min(el_costs)/lens[el_costs.index(min(el_costs))])
 # print(el_costs[12]/lens[gains.index(min(gains))])
 # print(el_costs[lens.index(min(lens))]/lens[0])
 # print(lens.index(min(lens)))
 # print(el_costs[0])
 # print(len(paths))
 # # print(poll_costs)
 # for u,v,a in poi.edges(data=True):
 #   print( a)
 # print(weather)
def extract_lng_lat(address_or_postalcode, data_type = 'json'):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/{data_type}"
    params = {"address": address_or_postalcode,"components":"country:egypt" ,"key":'AIzaSyCVlAzzx4LrOubBY5WlwJ5beJoehjISRUI'}
    url_params = urlencode(params)
    url = f"{endpoint}?{url_params}"
    r = requests.get(url)
    if r.status_code not in range(200, 299): 
        return {}
    latlng = {}
    try:
        latlng = r.json()['results'][0]['geometry']['location']
    except:
        pass
    return latlng.get("lng"), latlng.get("lat")
print(extract_lng_lat("City stars"))
@app.route("/")
def hello():
    return "Hello, World!"
@app.route('/users', methods=["GET", "POST"])
def users():
    print("users endpoint reached...")
    if request.method == "GET":
        with open("/Users/macbookair/basic-web-app-tutorial/backend/users.json", "r") as f:
            data = json.load(f)
            data.append({
                "username": "user4",
                "pets": ["hamster"]
            })
            return flask.jsonify(data)
    if request.method == "POST":
        received_data = request.get_json()
        print(f"received data: {received_data}")
        loc =extract_lng_lat( received_data['loc'])
        print(loc)
        des =extract_lng_lat( received_data['des'])
    
        print(des)
        # des = received_data['des']
       
        r=route(loc,des)
        lats=[]
        lons=[]
        for p in r :
            (x,y)=p
            lats.append(y)
            lons.append(x)
            

        return_data = {
            "status": "success",
            "loc": f"{loc}",
            "des":  f'{des}',
          "route":  f'{r}',
          "lats":   f'{lats}',
          "lons":   f'{lons}'
        }
        return flask.Response(response=json.dumps(return_data), status=201)

if __name__ == "__main__":
    app.run("localhost", 6969)

