#!/bin/env python
import os,sys

def change_ip():
  id_data = {}
  new_data = {}
  for i in range(0,6):
    po_name = "redis-%s" %i
    ID = os.popen("kubectl exec -ti %s -n wuda -- grep 'myself' /data/redis-cluster/nodes.conf | awk -F':' '{print $1}' | awk '{print $1}'" %po_name).read().split('\n')[0:-1][0]
    new_ip = os.popen("kubectl get pods %s -n wuda -o wide | awk '{print $6}'| grep -v IP"%po_name).read().split('\n')[0:-1][0]
    id_data[po_name] = ID
    new_data[po_name] = new_ip
  
  for pod_name in id_data.keys():
      for pn in id_data.keys():
        print "%s -------------> %s"%(id_data[pn],new_data[pn])
        os.system("kubectl exec -ti {po_name} -n wuda -- sed -i 's#{ID} \(.*\):6379#{ID} {new_ip}:6379#g' /data/redis-cluster/nodes.conf".format(ID=id_data[pn], new_ip=new_data[pn], po_name=pod_name))
        print "replacing {ip} to {new_ip} in the nodes.conf of {po_name}".format(ip=id_data[pn], new_ip=new_data[pn], po_name=pod_name)
      
      print "restart redis..."
      os.system("kubectl exec -ti %s -n wuda -- kill 1"%pod_name)

if __name__ == '__main__':
  run_number = os.popen("kubectl get po -n wuda -o wide | grep -v manage |grep redis | grep Running | wc -l").read().split('\n')[0:-1][0]
  print "pod of running currently is %s" %run_number
  if run_number < 6:
    sys.exit("please wait for pod to start...")
  else:
    print "failover..."
  change_ip()
