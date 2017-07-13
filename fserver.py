import sys
sys.path.append('/home/duncan/anaconda2/lib/python2.7/site-packages/')
import numpy as np
import json
from flask import Flask
import flask
import pandas as pd
import mapdata
app = Flask(__name__)

HOST = "http://127.0.0.1:5000/"
attr_hierarchy = mapdata.make_attr_hierarcy("Pancan12-mRNA")
print attr_hierarchy
@app.route('/mapid/<string:mapid>', methods=['GET'])
def root(mapid):

    md = mapdata.MapData(mapid)
    # going to need to change that...
    group = attr_hierarchy[None]
    md.set_attrs([group, "AKT_pathway_program"])
    md.set_group_table(group)
    next_subsets = md.get_subsets()
    urls = [url_maker(mapid, subset) for subset in
            next_subsets]
    gdf = md.get_group_table()

    dict_package = {}

    dict_package["x"] = gdf["x"].tolist()
    dict_package["y"] = gdf["y"].tolist()
    dict_package["size"] = gdf["Size"].tolist()
    dict_package["text"] = md.get_names()
    dict_package["name"] = mapid
    dict_package["color"] = gdf["AKT_pathway_program"].tolist()
    dict_package["expand_url"] = urls
    dict_package["cmax"] = gdf["AKT_pathway_program"].max()
    dict_package["cmin"] = gdf["AKT_pathway_program"].min()

    jsn =  json.dumps(dict_package)
    resp = flask.Response(jsn)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/mapid/<string:mapid>/space/<string:space>', methods=['GET'])
def space(mapid, space):
    ### Make a qstr out of space specification...
    xys = map(float, space.split(";"))
    qstr = "x > " + str(xys[0]) + " and x < " + str(xys[1]) +" and y > " + \
           str(xys[2]) + " and y < " + str(xys[3])

    name = "x > " + str(round(xys[0],1)) + " and x < " + str(round(xys[1],1)) \
           +" and y > " + str(round(xys[2],1)) + " and y < " \
           + str(round(xys[3],1))
    ### Make above pretty...

    md = mapdata.MapData(mapid)
    md.set_space_subset(qstr)
    gdf = md.get_table()

    dict_package = {}

    dict_package["x"] = gdf["x"].tolist()
    dict_package["y"] = gdf["y"].tolist()
    dict_package["size"] = np.repeat(1, gdf.shape[0]).tolist()
    dict_package["text"] = md.get_names()
    dict_package["name"] = name

    dict_package["expand_url"] = None

    jsn =  json.dumps(dict_package)
    resp = flask.Response(jsn)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/p12', methods=['GET'])
def ping():
    '''
    '''
    xy_df = pd.read_table(
            "/home/duncan/scatter/data/Pancan12.mRNA.openOrd.xys",
            index_col=0
            )

    dict_package = {}

    dict_package["x"] = xy_df["x"].tolist()
    dict_package["y"] = xy_df["y"].tolist()
    dict_package["x_range"] = xy_df["x"].max() - xy_df["x"].min()
    dict_package["y_range"] = xy_df["y"].max() - xy_df["y"].min()
    dict_package["names"] = xy_df.index.tolist()

    json_package =  json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/mapid/<string:mapid>/subset/<string:subset_str>/group'
           '/<string:attrid>/attribute/<string:get_attr>',
           methods=['GET'])
def group_getter_with_attr(mapid, subset_str, attrid, get_attr):
    '''
    '''
    md = mapdata.MapData(mapid)
    md.set_attrs_from_subset(subset_str)
    md.set_attrs([attrid, get_attr])
    md.set_subset(subset_str)
    md.set_group_table(attrid)
    next_subsets = md.get_subsets()
    """
    you were here trying to get the url maker to perform correctly
    test is that you want to hit the root and make sure you always
    get something back in all urls that come over the wire in the
    expand_url field
    thanks have a nice day today, its going to be great!
    """
    urls = [url_maker(mapid, subset) for subset in
            next_subsets]

    gdf = md.get_group_table()

    dict_package = {}

    dict_package["x"] = gdf["x"].tolist()
    dict_package["y"] = gdf["y"].tolist()
    dict_package["size"] = gdf["Size"].tolist()
    dict_package["text"] = md.get_names()
    dict_package["name"] = md.get_name_from_subset()
    dict_package["expand_url"] = urls
    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/mapid/<string:mapid>/subset/<string:subset_str>/group'
           '/<string:attrid>',
           methods=['GET'])
def group_getter(mapid, subset_str, attrid):
    '''
    '''
    md = mapdata.MapData(mapid)
    md.set_attrs_from_subset(subset_str)
    md.set_attrs([attrid])
    md.set_subset(subset_str)
    md.set_group_table(attrid)
    next_subsets = md.get_subsets()
    """
    you were here trying to get the url maker to perform correctly
    test is that you want to hit the root and make sure you always
    get something back in all urls that come over the wire in the
    expand_url field
    thanks have a nice day today, its going to be great!
    """
    urls = [url_maker(mapid, subset) for subset in
            next_subsets]

    gdf = md.get_group_table()

    dict_package = {}

    dict_package["x"] = gdf["x"].tolist()
    dict_package["y"] = gdf["y"].tolist()
    dict_package["size"] = gdf["Size"].tolist()
    dict_package["text"] = md.get_names()
    dict_package["name"] = md.get_name_from_subset()
    dict_package["expand_url"] = urls
    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/mapid/<string:mapid>/subset/<string:subset_str>',
           methods=['GET'])
def subset_getter(mapid, subset_str):
    '''
    '''
    md = mapdata.MapData(mapid)
    md.set_attrs_from_subset(subset_str)
    md.set_subset(subset_str)
    """
    you were here trying to get the url maker to perform correctly
    test is that you want to hit the root and make sure you always
    get something back in all urls that come over the wire in the
    expand_url field
    thanks have a nice day today, its going to be great!
    """

    df = md.get_table()

    dict_package = {}

    dict_package["x"] = df["x"].tolist()
    dict_package["y"] = df["y"].tolist()
    dict_package["size"] = np.repeat(1, df.shape[0]).tolist()
    dict_package["text"] = md.get_names()
    dict_package["name"] = md.get_name_from_subset()
    dict_package["expand_url"] = None
    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'


    return resp

@app.route('/GtexGM', methods=['GET'])
def ping2():
    '''
    '''
    xy_df = pd.read_table(
            "/home/duncan/scatter/server/data/GtexGeneMapXY.tab",
            index_col=0
            )

    dict_package = {}

    dict_package["x"] = xy_df["x"].tolist()
    dict_package["y"] = xy_df["y"].tolist()
    dict_package["text"] = xy_df.index.tolist()

    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/groupprac', methods=['GET'])
def ping5():
    '''
    '''
    md = mapdata.MapData()
    md.set_attrs(["Tissue"])
    md.set_group_table("Tissue")
    gdf = md.get_group_table()

    dict_package = {}

    dict_package["x"] = gdf["x"].tolist()
    dict_package["y"] = gdf["y"].tolist()
    dict_package["size"] = gdf["Size"].tolist()
    dict_package["text"] = md.get_names()


    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/expandprac', methods=['GET'])
def ping6():
    '''
    '''
    md = mapdata.MapData()
    md.set_attrs(["Tissue", "hdb_cluster"])
    subset_str = 'Tissue==BRCA'

    md.set_subset(subset_str)
    gdf = md.get_table()

    dict_package = {}

    dict_package["x"] = gdf["x"].tolist()
    dict_package["y"] = gdf["y"].tolist()
    dict_package["size"] = np.repeat(1, gdf.shape[0]).tolist() # gdf[
    # "Size"].tolist()
    dict_package["text"] = gdf.index.tolist()

    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/1mil', methods=['GET'])
def ping3():
    '''
    '''
    xy_df = pd.read_table(
            "/home/duncan/scatter/data/1mil.rand.xy.tab",
            index_col=0
            )

    dict_package = {}

    dict_package["x"] = xy_df["x"].tolist()
    dict_package["y"] = xy_df["y"].tolist()
    dict_package["names"] = xy_df.index.tolist()

    json_package = json.dumps(dict_package)

    resp = flask.Response(json_package)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

def url_maker(mapid, subset):
    try:
        group = attr_hierarchy[subset]
    except KeyError:
        group = None

    if group is None:
        url = HOST + "mapid/" + mapid + "/subset/" + subset
    else:
        url = HOST + "mapid/" + mapid + "/subset/" + subset + "/group/" + group

    return url

if __name__ == '__main__':
    app.run()
