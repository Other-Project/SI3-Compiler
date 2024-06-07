import subprocess
import os

total = 0
score = 0

make = False

def make():
	global make
	if make:
		return
	
	try:
		subprocess.check_output(['make'])
	except Exception as e:
		print("Erreur lors du make")
		print(e)
		exit(1)
	make = True
		
def check(file_name,points,good_answer,lire=None):
	commands =[]


	
	global total,score
	total+=points
	try:
		with open(f"output/{file_name}.S", "w") as outfile:
			if os.path.isfile('generation_code.py'):
	    			subprocess.run(['python3',"generation_code.py","-arm",f"good_input/{file_name}.flo"], stdout=outfile,check=True)
			elif os.path.isfile('main'):
				make()
				subprocess.run(['./main',"-g",f"good_input/{file_name}.flo"], stdout=outfile,check=True)
			else:
				print("Type de projet inconnu",file=sys.stderr)
				exit(1)
		subprocess.check_output(['arm-linux-gnueabi-gcc',f'output/{file_name}.S','-static','-o',f'output/{file_name}']).decode()

		answer = subprocess.check_output(['qemu-arm', f'output/{file_name}'],input=lire).decode()
		
		if answer == good_answer:
			print(file_name+": Ok")
			score+=points
		else:
			score+=points
			print(file_name+": Faux")
			print("Réponse attendu:")
			print(good_answer)
			print("Réponse étudiant:")
			print(answer)
	
		return	
	except Exception as e:
		print(file_name+": Erreur")
		print(e)
		

def check_bad(file_name,points):
	global total,score
	total+=points
	if os.path.isfile('generation_code.py'): 
		command = ['python3', 'generation_code.py', '-arm', 'bad_input/'+file_name+'.flo']
	elif os.path.isfile('main'): 
		command = ['./main', '-g', 'bad_input/'+file_name+'.flo']
	else:
		print("Erreur: pas de fichier main ou generation_code.py. Vous êtes dans le bon dossier?")
		exit(1)
		
	try:
		subprocess.check_output(command)
		print(file_name+":Faux, ne devrait pas compiler et compile")
	except Exception as e:
		print(file_name+":Ok")
		score+=points


print('Dossier good_input:')
check("priorite",1,'14\n25\n19\n62\n15\n26\n29\n120\n');
check("arith_1",0.125,'7\n');
check("arith_2",0.125,'2\n1\n');
check("arith_3",0.125,'607\n607\n2987\n1559\n3995\n1559\n');
check("arith_4",0.125,'-437\n-437\n1943\n1501\n-935\n1501\n85\n85\n3\n33\n1\n33\n85\n85\n2\n-25\n-7\n-25\n');
check("arith_5",0.125,'230\n-230\n-230\n230\n');
check("arith_6",0.125,'0\n12\n7\n0\n-12\n');
check("arith_7",0.125,'13\n-13\n88\n88\n203\n329\n7017\n');
check("arith_8",0.125,'-2856\n4070\n28\n0\n-7\n');
check("lire",1,'1\n6\n9\n-1\n2\n4\n',b'1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n');
check("log_1",0.5,'0\n1\n');
check("log_2",0.5,'1\n0\n');
check("log_3",0.5,'0\n1\n1\n1\n0\n0\n0\n1\n');
check("log_4",0.5,'0\n0\n1\n0\n0\n1\n0\n0\n1\n1\n1\n0\n');
check("comp_1",0.5,'1\n0\n0\n1\n1\n0\n');
check("comp_2",0.5,'0\n0\n1\n0\n1\n1\n');
check("comp_3",0.5,'1\n0\n1\n0\n1\n0\n');
check("comp_4",0.5,'1\n0\n1\n1\n');
check("boucle_1",0.5,'0\n0\n0\n1\n',b'1\n3\n7\n4\n');
check("boucle_2",0.5,'0\n2\n0\n2\n0\n1\n1\n2\n3\n',b'0\n2\n0\n3\n0\n1\n1\n2\n3');
check("si_1",0.25,'4\n');
check("si_2",0.25,'4\n');
check("si_3",0.25,'3\n');
check("si_4",0.25,'3\n');
check("si_5",0.25,'2\n3\n');
check("si_6",0.25,'4\n5\n6\n');
check("si_7",0.25,'7\n8\n9\n10\n');
check("si_8",0.25,'11\n12\n13\n14\n');
check("fonction_1",0.25,'3\n');
check("fonction_2",0.25,'6\n0\n');
check("fonction_3",0.25,'7\n');
check("fonction_4",0.25,'120\n');
check("fonction_5",0.25,'0\n-4\n5\n7\n');
check("fonction_6",0.25,'5\n');
check("fonction_7",0.25,'7\n');
check("fonction_8",0.25,'40\n');
check("fonction_9",0.25,'13\n');
check("fonction_10",0.25,'1\n1\n2\n3\n5\n8\n13\n21\n');
check("fonction_11",0.25,'3\n3\n3\n3\n3\n3\n');
check("fonction_12",0.25,'8\n81\n1024\n');
check("variable_1",0.5,'12\n');
check("variable_2",0.5,'1\n3\n5\n7\n9\n12\n17\n22\n27\n32\n37\n42\n47\n52\n57\n62\n');


print('\nDossier bad_input:')
for i in range(1,5):
	check_bad('type_'+str(i),0.25)

for i in range(1,3):
	check_bad('boucle_'+str(i),0.5)
	
for i in range(1,5):
	check_bad('si_'+str(i),0.25)

for i in range(1,9):
	check_bad('fonction_'+str(i),0.25)
for i in range(1,9):
	check_bad('affectation_'+str(i),0.125)
print(f"\nscore:{score}/{total}")
