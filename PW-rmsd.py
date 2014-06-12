#!/usr/bin/env python


import MDAnalysis
import MDAnalysis.analysis
from MDPackage import Index
from MDPackage import Simple_atom
# from MDPackage import usage
import os
import sys
import getopt
import numpy

def Usage():
	print "Usage: PW-rmsd.py -p <coor_file> -f <traj_file> -n <ndx_file> -o rmsd.xvg --skip 1"
	print "Usage: PW-rmsd.py -i input.in -n <ndx_file> -o rmsd.xvg --skip 1"


def Traj_2_rms(coor_list,traj_list,rmsd_file,atom_list,skip):
	'''
	Reading a trajectory file. output the pairwiseRMSD to rmsd_file.\n
	atom_list : a list of atom serial.\n
	skip: a int number like 1,2,3,10. 
	'''
	Alist=Simple_atom.Get_Simple_atom_list(coor_list[0])
	Blist=[]
	for atom in Alist:
		if atom.atom_serial in atom_list:
			Blist.append(atom)
	'''Get the result atom list in Simple_atom class.'''

	if os.path.isfile(rmsd_file):
		print "backup %s to %s\n " %(rmsd_file,"#"+rmsd_file+"#")
		try:
			os.rename(rmsd_file,"#"+rmsd_file+"#")
		except OSError,e: 
			print e
			print "the file %s will be overwrited!" %rmsd_file
	fp=open(rmsd_file,'w+')
	traj_data=list()

	for i,coor_file in enumerate(coor_list):
		u=MDAnalysis.Universe(coor_list[i],traj_list[i])
		# print len(Blist)
		for ts in u.trajectory:
			if ts.frame % skip ==0 :
				temp_array=numpy.zeros([len(Blist),3],numpy.float32)
				# print numpy.shape(temp_array)
				sys.stderr.write("Loading frame %10d\r" %(ts.frame))
				sys.stderr.flush()
				for i,atom in enumerate(Blist):
					temp_array[i,0]=ts._x[atom.atom_serial-1]
					temp_array[i,1]=ts._y[atom.atom_serial-1]
					temp_array[i,2]=ts._z[atom.atom_serial-1]
				average=[sum(temp_array[:,i])/len(Blist) for i in range(3)]
				# print average
				for i in range(len(Blist)):
					# print "before,",temp_array[i]
					temp_array[i]=temp_array[i]-average
					# print "after,",temp_array[i] 
				# sys.exit()
				# print temp_array[0]
				traj_data.append(temp_array)
			else:
				pass
		print ""

	# rmsd_matrix=list()
	print "write 2D RMSD  result to file %s. please wait..." %rmsd_file
	for i,a in enumerate(traj_data):
		for j,b in enumerate(traj_data):
			va=MDAnalysis.analysis.rms.rmsd(a,b)
			fp.write("%f %f %f\n" %(i,j,va))
		fp.write("\n")
			# rmsd_matrix.append([i,j,va])

	# for i,a in enumerate(rmsd_matrix):
	# 	if a[0]!=rmsd_matrix[i-1][0] and i > 0:
	# 		fp.write("\n")
	# 	fp.write("%f %f %f\n" %(a[0],a[1],a[2]))
	fp.close()


	# print rmsd_matrix
	# return True


def main():

	try:
		opts,args=getopt.getopt(sys.argv[1:],"p:f:n:o:i:h",["skip=","begin=","end="])
	except getopt.GetoptError,e:
		print e
		sys.exit()

	skip=1
        input_file = ""

	for a,b in opts:
		if a=="-p":
			coor_file=b
		elif a=="-f":
			traj_file=b
		elif a=="-n":
			ndx_file=b
		elif a=="-o":
			rmsd_file=b
		elif a=="-i":
			input_file=b
		elif a=="--skip":
			skip=int(b)
		elif a=="-h":
			Usage()
			sys.exit()

	try:
		index_list=Index.Read_index_to_Inclass(ndx_file)
	except:
		print "Error in reading index file."
		print "Using -h to see usage."
		sys.exit()
	Index.Print_Index(index_list)
	group_ID=raw_input("Choose a group: ")
	try:
		atom_list=index_list[int(group_ID)].group_list
	except:
		print "error"
		sys.exit()

	if os.path.isfile(input_file):
		coor_list=list()
		traj_list=list()
		ip=open(input_file)
		lines=ip.readlines()
		ip.close()
		for line in lines:
			temp=line.split()
			if os.path.isfile(temp[0]) and os.path.isfile(temp[1]):
				coor_list.append(temp[0])
				traj_list.append(temp[1])
			else:
				print "Error: coor_file %s or traj_file %s not found." %(temp[0],temp[1])
		Traj_2_rms(coor_list,traj_list,rmsd_file,atom_list,skip)
	else:
		Traj_2_rms([coor_file],[traj_file],rmsd_file,atom_list,skip)


if __name__ == '__main__':
	main()
