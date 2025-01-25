import socket
from bencode import bencode, bdecode
import sys
import random
import select
import struct
import time

if len(sys.argv) < 3:
	print('usage: %s host port' % sys.argv[0])
	sys.exit(1)

def send_dht_message(msg, target):
	global s
	#try:
	print("--> ", target[0], target[1])
	s.sendto(bencode(msg), 0, target)
	#except Exception as e:
	#	print(e)

def random_key():
	return random.randbytes(20)

# returns a list of tuples (list-of-nodes, client-name, ip)
def scrape_dht_nodes(query, nodelist):
	global node_id
	global s

	tid = random.randint(0, 65536)

	msg = {b'a': {b'id': node_id}, b'q': query.encode('ascii'), b'y': 'q', b'ro':1, b't': '%d' % tid}
	if query == 'find_node':
		msg[b'a'][b'target'] = random_key()
	elif query == 'get_peers':
		msg[b'a'][b'info-hash'] = random_key()
	elif query == 'ping':
		pass
	else:
		print('ERROR: invalid query "%s"' % query)
		return []

	for n in nodelist:

		send_dht_message(msg, (n['ip'], n['port']))
		time.sleep(0.01)

	num_replies = len(nodelist)

	responses = []
	start_time = time.time()
	timed_out = False

	while num_replies > 0:
		timeout = start_time + 3 - time.time()
		if timeout <= 0: timeout = 0
		n = select.select([s], [], [s], timeout)
		if len(n[0]) == 0:
			if timeout == 0: break
			timed_out = True
			num_replies -= 1
			continue
		# the socket became readable
		response, addr = s.recvfrom(1500)
		#try:
		response = bdecode(response)
		#	if response[b'y'] != b'r':
		#		print('ERROR: expected a response, received %s' % response)
		#		continue
		#except:
		#	print('ERROR: ', response)
		#	continue

		try:
			t = int(response[b't'])
			# this is not the transaction id we sent
			if t != tid: continue
		except:
			# invalid transaction id
			continue

		num_replies -= 1

		try:
			v = response[b'v']
		except:
			v = b''
			pass

		if len(v) == 4:
			(name, v1) = struct.unpack('<2sH', v)
			client = '%s-%d' % (name, v1)
		else:
			client = v

		try:
			nodes_str = response[b'r'][b'nodes']
		except:
			responses.append(([], client, addr))
			continue

		nodes = []
		while len(nodes_str) >= 26:
			(nid, ip, port) = struct.unpack('>20s4sH', nodes_str[:26])
			nodes.append({'ip': socket.inet_ntoa(ip), 'port': port, 'id': nid})
			nodes_str = nodes_str[26:]

		responses.append((nodes, client, addr))

	return responses

# this is our node-id
node_id = random_key()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

live_nodes = []

clients = {}

total_timeout = 0
total_response = 0

target_ip = socket.gethostbyname(sys.argv[1])
target_port = int(sys.argv[2])

print(target_ip)
print(target_port)

for i in range(500):
	responses = scrape_dht_nodes('find_node', [ { 'ip': target_ip, 'port': target_port } ])

	if len(responses) == 0:
		print('router timeout')
		continue

	nodes = []
	for r in responses:
		nodes += r[0]

	response_ip = []

	num_pings = len(nodes)
	responses = scrape_dht_nodes('find_node', nodes)
	for r in responses:
		nodes += r[0]
		response_ip.append(r[2])
		live_nodes.append(r[2])
		c = r[1][:2]
		if c in clients: clients[c] += 1
		else: clients[c] = 0

	print('<-- responses: %d timeouts: %d ips: ' % (len(responses), num_pings - len(responses)), end="")
	total_response += len(responses)
	total_timeout += num_pings - len(responses)

	for ip in response_ip:
		print('%s,' % ip[0], end="")
	print()
	time.sleep(0.3)

print('total-up: %d total-down: %d alive-ratio: %f%%' % (total_response, total_timeout, total_response * 100.0 / float(total_response + total_timeout)))

for i in live_nodes:
	print(i[0])

print(clients)
