#!/usr/bin/env python

"""
/*
 * Copyright (C) 2016 Rich Burton
 *
 * This file is part of hooperfly open-source.
 *
 * hooperfly open-source is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * hooperfly open-source is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with hooperfly open-source; see the file COPYING.  If not, see
 * <http://www.gnu.org/licenses/>.
 */
"""

from __future__ import print_function
import sys
from os import path, getenv
import os
import time
import argparse
from flask import Flask, request, Response, render_template
import json
from itertools import cycle

from math import radians


app = Flask(__name__)

# --- Configure server logging levels

# Only spit out error level server messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- Class/Global state variables

lbc_version   = "0.0.1"
verbose       = 0              # Default is disabled(i.e. = 0)
curl          = 0              # Default is disabled(i.e. = 0)
subscribe     = 0              # Default is disabled(i.e. = 0)
server_host   = "127.0.0.1"    # Default to local host)
server_port   = 5000           # Default it flask port)
server_host_prefix = "127.0.0."

# --- Bucket and Lighblock related state/methods


class Lightblock(object):
    def __init__(self, lb_id, lb_name):
        self.lb_id   = lb_id
        self.lb_name = lb_name

class Bucket(object):
    def __init__(self, bc_id, name, color):
        self.bc_id        = bc_id
        self.name         = name
        self.color        = color
        self.lightblocks = {}
 
buckets = {}

def add_new_bucket_lightblock( bucket, lb_id, lb_name):
    bucket.lightblocks[lb_id] = Lightblock(lb_id, lb_name)      

def add_new_bucket(bc_id, name, color):
    buckets[bc_id] = Bucket(bc_id, name, color)

def print_bucket_data():
    for bc_id in buckets:
        print( bc_id, buckets[bc_id].name, buckets[bc_id].color )
        for lb_id in buckets[bc_id].lightblocks:
            print( lb_id, buckets[bc_id].lightblocks[lb_id].lb_name )

def generate_configuration_stub():
    tmp_bc_id = 0   # Assuming all bucket use the same flight plan, we cache an bucket index
    curline = ''

    print('<client>')

    label = 1
    for bc_id in buckets:
        curline = '    <bucket name="%s" color="%s" label="%d" icon="" tooltip="%s" />' % (buckets[bc_id].name, buckets[bc_id].color, label, buckets[bc_id].name)
        print( curline  )
        label += 1
        tmp_bc_id = bc_id

    color = cycle(['lime', 'green', 'deepskyblue', 'dodgerblue', 'yellow', 'gold', 'orange', 'darkorange', 'orangered', 'red', 'darkred'])
    label = 1
    for lb_id in buckets[tmp_bc_id].lightblocks:
        curline = '    <lightblock name="%s" color="%s" label="%d" icon="" tooltip="%s" />' % (buckets[tmp_bc_id].lightblocks[lb_id].lb_name, color.next(), label, buckets[tmp_bc_id].lightblocks[lb_id].lb_name)
        print( curline )
        label += 1

    color = cycle(['deepskyblue', 'dodgerblue', 'lime', 'green', 'gold', 'orange', 'orangered', 'red'])
    
    print('</client>')


bucket_client_list       = []   # Used for rows in client; preserve list order
lightblock_client_list    = []   # Used for columns in client view for lightblocks; preserve list order
#lb_color_list              = ['lime', 'green', 'deepskyblue', 'dodgerblue', 'yellow', 'gold', 'orange', 'darkorange', 'orangered', 'red', 'darkred']
#gd_color_list              = ['magenta', 'purple', 'deepskyblue', 'dodgerblue', 'lime', 'green', 'gold', 'orange', 'orangered', 'red']
#wp_color_list              = ['deepskyblue', 'dodgerblue', 'lime', 'green', 'gold', 'orange', 'orangered', 'red']

bc_color_list              = []   # Used by bucket view color cycler
bc_label_list              = []   # Used by bucket view label cycler
bc_icon_list               = []   # Used by bucket view icon cycler
bc_tooltip_list            = []   # Used by bucket view tooltip cycler

lb_color_list              = []   # Used by flight block view color cycler
lb_label_list              = []   # Used by flight block view label cycler
lb_icon_list               = []   # Used by flight block view icon cycler
lb_tooltip_list            = []   # Used by flight block view tooltip cycler


# --- Helper methods ---

def print_curl_header(host, port):
    print('#!/bin/bash')
    print('host=%s' % host)
    print('port=%s' % port)

def print_curl_format():
    #print('curl %s' % request.url)
    print('curl http://$host:$port%s' % request.path)

def print_curl_trace(msg):
    print("Sending curl message interface: %s" % msg)

from lxml import etree  as ET    

def view_attributelist_helper(view, view_color_list, view_label_list, view_icon_list, view_tooltip_list):
    color = view.get('color')
    if color:  # Add it to the flight block color list, TODO: possibly add color attribute to lightblock object
        view_color_list.append(color)
    else:
        view_color_list.append('white') # if the color list is empty set the default to white
    label = view.get('label')
    if label:
        view_label_list.append(label)
    else:
        view_label_list.append('')            
    icon = view.get('icon')
    if icon:
        view_icon_list.append(icon)
    else:
        view_icon_list.append('')
    tooltip = view.get('tooltip')
    if tooltip:
        view_tooltip_list.append(tooltip)
    else:
        view_tooltip_list.append('')

def static_init_configuration_data():
    tree = ET.parse('conf.xml')
    root = tree.getroot()

    # Populate aircraft objects
    for bucket in root.findall('bucket'):
        bcid           = int(bucket.get('id'))
        name           = bucket.get('name')
        color          = bucket.get('color')
        add_new_bucket(bcid, name, color)
        print("Bucket id: %d" % bcid)
        bucket = buckets[bcid]
    
        # Process lightblocks
        for idx, block in enumerate(root.iter('block')):
            name = block.get('name')
            add_new_bucket_lightblock(bucket, idx, name)


def static_init_client_configuration_data(fname):
    tree = ET.parse(fname)
    root = tree.getroot()
    tmp_bc_id = 0   # Assuming all bucket use the same flight plan, we cache an bucket index

    # Populate bucket client objects
    for bucket in root.findall('bucket'):
        bc_id = int(bucket.get('bc_id')) if bucket.get('bc_id') else None
        name  = bucket.get('name')
        if name: 
            bc_id = next((idx for idx in buckets if buckets[idx].name == name), None)
            print("Found bucket name: %s" % buckets[bc_id].name)
        color = bucket.get('color')
        if color:  #Override current conf.xml gui_color value if defined in lbc_conf.xml
            buckets[bc_id].color = color
        # TODO: Add conf.xml colors to these structures if the color attribute is not specified in lbc_conf.xml
        view_attributelist_helper(bucket, bc_color_list, bc_label_list, bc_icon_list, bc_tooltip_list)
        bucket_client_add(bc_id)
        tmp_bc_id = bc_id  # Cache the current bucket index for use in lightblock search

    # Populate lightblock client objects
    for lightblock in root.findall('lightblock'):
        lb_id = int(lightblock.get('lb_id')) if lightblock.get('lb_id') else None
        name = lightblock.get('name')
        if name: 
            lb_id = next((idx for idx in buckets[tmp_bc_id].lightblocks if buckets[tmp_bc_id].lightblocks[idx].lb_name == name), None)
            print("Found lightblock name: %s" % buckets[tmp_bc_id].lightblocks[lb_id].lb_name)
        view_attributelist_helper(lightblock, lb_color_list, lb_label_list, lb_icon_list, lb_tooltip_list)
        lightblock_client_add(lb_id)
    

# --- Routes/Paths ----

@app.route('/')
def index():
    retval = 'Light Bucket Commander Server Running....'

    if verbose: 
        retval = 'Light Bucket Commander Server Running....\n'
    if curl: print_curl_format()
    return retval


@app.route('/bucket/')
def bucket_all():
    aclist = []
    for bc_id in buckets:
        aclist.append(bc_id)
    if curl: print_curl_format()
    return str(aclist)


@app.route('/bucket/<int:bc_id>')
def bucket(bc_id):
    bc_id = int(bc_id)
    if bc_id in buckets:
        alist = []
        alist.append(bc_id)
        alist.append(buckets[bc_id].name)
        alist.append(buckets[bc_id].color)
        for lb_id in buckets[bc_id].lightblocks:
            alist.append(lb_id)   
            alist.append(buckets[bc_id].lightblocks[lb_id].lb_name)   
        if curl: print_curl_format()
        return str(alist)    
    return "unknown id"    


@app.route('/bucket/client/')
def bucket_client_all():
    if curl: print_curl_format()
    return str(bucket_client_list)


@app.route('/bucket/client/add/<int:bc_id>')
def bucket_client_add(bc_id):
    bc_id = int(bc_id)
    if bc_id in buckets:
        if bc_id not in bucket_client_list:       
            bucket_client_list.append(bc_id)
        if curl: print_curl_format()
        return str(bucket_client_list)    
    return "unknown bucket id"    


@app.route('/lightblock/noop/')
def lightblock_noop():
    if curl: print_curl_format()
    return "noop"


@app.route('/lightblock/client/')
def lightblock_client_all():
    if curl: print_curl_format()
    return str(lightblock_client_list)


@app.route('/lightblock/client/add/<int:lb_id>')
def lightblock_client_add(lb_id):
    if bucket_client_list:
        lb_id = int(lb_id)
        if lb_id in buckets[bucket_client_list[0]].lightblocks:  # KLUDGE: Use first defined bucket's lightblocks to verify, assume all bucket use same flight plan
            if lb_id not in lightblock_client_list:       
                lightblock_client_list.append(lb_id)
            if curl: print_curl_format()
            return str(lightblock_client_list)    
        return "unknown lightblock id"
    return "bucket list is empty"    




@app.route('/lightblock/<int:bc_id>/<int:lb_id>')
def lightblock(bc_id, lb_id):
    retval = ''

    rqst = 'http://%s%d/?sequence=%s' % (server_host_prefix, bc_id, buckets[bc_id].lightblocks[lb_id].lb_name)
    print( 'request: %s' % rqst )
    #os.system( "curl %s" % (rqst) )
    if curl: print_curl_format()
    return retval


@app.route('/lightblock/<int:lb_id>')
def lightblock_all_bucket(lb_id):
    retval = ''

    for bc_id in bucket_client_list:
        rqst = 'http://%s%d/?sequence=%s' % (server_host_prefix, bc_id, buckets[bc_id].lightblocks[lb_id].lb_name)
        print( 'request: %s' % rqst )
        #os.system( "curl %s &" % (rqst) )
    if curl: print_curl_format()
    return retval


@app.route('/template/configuration/')
def template_configuration():
    generate_configuration_stub()
    return
 

@app.route('/show/view/<name>/')
def showview(name):
    view_mode   = request.args.get('view_mode',  'col')
    button_size = request.args.get('button_size', 64) 
    return render_template(name+'.html', p_host=server_host,          p_port=server_port, 
                            p_row_count=len(bucket_client_list),    p_row_list=bucket_client_list, 
                            p_bc_color_list=bc_color_list,            p_bc_label_list=bc_label_list,
                            p_bc_icon_list=bc_icon_list,              p_bc_tooltip_list=bc_tooltip_list,
                            p_view_mode=view_mode,                    p_button_size=int(button_size),
                            p_col_count=len(lightblock_client_list), p_col_list=lightblock_client_list,
                            p_color_list=lb_color_list,               p_label_list=lb_label_list,
                            p_icon_list=lb_icon_list,                 p_tooltip_list=lb_tooltip_list)


@app.route('/show/lightblock/')
def showlightblock():
    view_mode   = request.args.get('view_mode',   'col')
    button_size = request.args.get('button_size', 64) 
    return render_template('lightblock.html', p_host=server_host,    p_port=server_port, 
                            p_row_count=len(bucket_client_list),    p_row_list=bucket_client_list, 
                            p_bc_color_list=bc_color_list,            p_bc_label_list=bc_label_list,
                            p_bc_icon_list=bc_icon_list,              p_bc_tooltip_list=bc_tooltip_list,
                            p_view_mode=view_mode,                    p_button_size=int(button_size),
                            p_col_count=len(lightblock_client_list), p_col_list=lightblock_client_list,
                            p_color_list=lb_color_list,               p_label_list=lb_label_list,
                            p_icon_list=lb_icon_list,                 p_tooltip_list=lb_tooltip_list)


@app.route('/about')
def about():
    return 'About: Light Bucket Commander Server v%s\n' % (lbc_version)


# --- Main body ----
if __name__ == '__main__':

    # Get/set the required IP address and port number along with other command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1",
                        help="ip address")
    parser.add_argument("-p","--port", type=int, default=5000,
                        help="port number")
    parser.add_argument("-f","--file", type=str, default="lbc_conf.xml",
                        help="use the specified client configuration file")
    parser.add_argument("-g","--generate",  action="store_true", help="generate a client configuration stub")
    parser.add_argument("-c","--curl",      action="store_true", help="dump actions as curl commands")
    parser.add_argument("-v","--verbose",   action="store_true", help="verbose mode")

    try:
        # --- Startup state initialization block
        args = parser.parse_args()
        static_init_configuration_data()
        static_init_client_configuration_data(args.file)
        if args.verbose: 
            print_bucket_data()
        if args.generate:
            template_configuration()
            sys.exit(0)

        # Handle misc. command line arguments
        if args.verbose: 
            verbose=args.verbose
        if args.curl: 
            curl=args.curl
            print_curl_header(args.ip, args.port)

        # --- Main loop
        # Supply flask the appropriate ip address and port for the server
        server_host = args.ip      # Store for use in htlm template generation
        server_port = args.port    # Store for use in htlm template generation

        a, b, c, d = server_host.split(".")
        server_host_prefix = a + '.' + b + '.' + c + '.'

        app.run(host=args.ip,port=args.port,threaded=True)

    except Exception as e:
        print(e)
        sys.exit(0)
