#!/usr/bin/env python
import subprocess
import optparse
import json
import os
import re

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class metrics(BaseHTTPRequestHandler):

        def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type','text/plain; version=0.0.4')
                self.end_headers()
                # fetch alfred data
                call159 = subprocess.check_output(['alfred-json','-z','-f','json','-r','159','-s',options.socket_path])
                call158 = subprocess.check_output(['alfred-json','-z','-f','json','-r','158','-s',options.socket_path])
                call160 = subprocess.check_output(['alfred-json','-z','-f','json','-r','160','-s',options.socket_path])
                # convert json
                config = json.loads(call159.decode('utf-8'))
                config2 = json.loads(call158.decode('utf-8'))
                config3 = json.loads(call160.decode('utf-8'))
                # webserver displays
                self.wfile.write('# A.L.F.R.E.D. Prometheus exporter - Metrics from mesh networks' + '\n')
                self.wfile.write('#' + '\n')

                neighbours = {}

                for mac in config2:
                        if 'mesh_interfaces' in config2[mac]['network']:
                                for mesh in config2[mac]['network']['mesh_interfaces']:
                                        neighbours[mesh] = str(config2[mac]['hostname'])

                for mac in config:
                        try:
                                cpu_load = 'ffnode_stats_load{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['loadavg'])
                                cpu_load = re.sub('[!@$:]', '', cpu_load)
                                self.wfile.write(cpu_load)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                mem_total = 'ffnode_stats_memory_total{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['memory']['total'])
                                mem_total = re.sub('[!@$:]', '', mem_total)
                                self.wfile.write(mem_total)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                mem_free = 'ffnode_stats_memory_free{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['memory']['free'])
                                mem_free = re.sub('[!@$:]', '', mem_free)
                                self.wfile.write(mem_free)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                clients_total = 'ffnode_stats_clients{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['clients']['total'])
                                clients_total = re.sub('[!@$:]', '', clients_total)
                                self.wfile.write(clients_total)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                node_uptime = 'ffnode_stats_uptime{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['uptime'])
                                node_uptime = re.sub('[!@$:]', '', node_uptime)
                                self.wfile.write(node_uptime)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                net_receive = 'ffnode_network_bytes_receive{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['traffic']['rx']['bytes'])
                                net_receive = re.sub('[!@$:]', '', net_receive)
                                self.wfile.write(net_receive)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                net_transmit = 'ffnode_network_bytes_transmit{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['traffic']['tx']['bytes'])
                                net_transmit = re.sub('[!@$:]', '', net_transmit)
                                self.wfile.write(net_transmit)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                mgmt_receive = 'ffnode_network_bytes_mgmt_receive{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['traffic']['mgmt_rx']['bytes'])
                                mgmt_receive = re.sub('[!@$:]', '', mgmt_receive)
                                self.wfile.write(mgmt_receive)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                mgmt_transmit = 'ffnode_network_bytes_mgmt_transmit{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['traffic']['mgmt_tx']['bytes'])
                                mgmt_transmit = re.sub('[!@$:]', '', mgmt_transmit)
                                self.wfile.write(mgmt_transmit)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
                                net_forward = 'ffnode_network_bytes_forward{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+'"} '+str(config[mac]['traffic']['forward']['bytes'])
                                net_forward = re.sub('[!@$:]', '', net_forward)
                                self.wfile.write(net_forward)
                                self.wfile.write('\n')
                        except KeyError:
                                pass
                        try:
				for interface in config3[mac]['batadv']:
                                        for neighbour in config3[mac]['batadv'][interface]['neighbours']:
                                                if neighbours[neighbour] != '':
                                                        neigh_name = re.sub('[!@$:]', '', neighbours[neighbour])
                                                        batadv_neigh = 'ffnode_stats_neighbours{node_id="'+str(mac)+'",hostname="'+str(config2[mac]['hostname'])+',neighbour="'+str(neigh_name)+'"} '+str(config3[mac]['batadv'][interface]['neighbours'][neighbour]['tq'])
                                                        batadv_neigh = re.sub('[!@$:]', '', batadv_neigh)
                                                        self.wfile.write(batadv_neigh)
                                                        self.wfile.write('\n')
                        except KeyError:
                                pass
                return
                self.wfile.write("</html>")
                self.wfile.close()

parser = optparse.OptionParser()

parser.add_option('-p',
    action="store", dest="http_port",
    help="port to serve metrics via http. default=9205", default="9205")
parser.add_option('-s',
    action="store", dest="socket_path",
    help="path to alfred socket file.", default="/var/run/alfred.sock")

options, args = parser.parse_args()

WEB_PORT = int(options.http_port)

try:
        server = HTTPServer(('', WEB_PORT), metrics)
        print 'Started httpserver on port ' , WEB_PORT

        server.serve_forever()

except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()

