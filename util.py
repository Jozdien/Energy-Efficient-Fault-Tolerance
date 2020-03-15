import random
import matplotlib.pyplot as plt
from subprocess import call
import numpy as np

graph_utilization_ltf = []
graph_power_ltf = []
graph_utilization_ltf_us = []
graph_power_ltf_us = []
upper_limit = 70.0
lower_limit = 10.0

for i in range(int(lower_limit), int(upper_limit), 3):
	average_energy_total_ltf = 0
	average_energy_total_ltf_us = 0
	for j in range(1, 1000):
		for init in range(1): # Initializing everything
			f = open("simple.tgff", "r")
			s = f.readlines()
			f_h = 1.0
			f_l = 0.8
			threshold = 0.6
			d = 100
			tasks = 0
			s1 = []
			edges = []
			a_h = []
			a_l = []
			alpha_h = []
			alpha_l = []
			time_h = 0
			time_l = 0
			time_h_array = {}
			time_l_array = {}
			levels = ['0']
			level_tasks = []
			next_tasks = {}
			task_c_h = []
			task_w_h = []
			task_c_l = []
			task_w_l = []
			u_l = 0.0
			u_h = 0.0
			temp = []
			temp_dict = {}
			u_tasks = []
			total = 0
			power_l = []
			power_h = []
			power_ltf = []
			tightest = 0
			tightest_value = 1000
			order = []
			primary_contingency_finish = {}
			backup_contingency_start = {}
			core_finish_time_each_task = []
			l_total_time = 0
			h_total_time = 0
			power_l_total = 0
			power_h_total = 0
			ltf_us_power = 0
			energy_total = 0
			temp_task_c_h = []
			temp_task_c_l = []
			temp_task_w_h = []
			temp_task_w_l = []
		for line in s: # Number of tasks
			if line[0:5] == "	TASK":
				tasks = tasks + 1
		for line in s: # Extracting edges from file
			if line[0:4] == "	ARC":
				s1.append(line[11:])
		for edge in s1: # Splitting each edge to array "edges"
			desc = edge.split()
			desc = desc[1][3:] + " TO " + desc[3][3:]
			edges.append(desc)
		for task in range(tasks): # Generating c and w for HP and LP
			c_h = round(random.uniform(0.1,70/tasks), 1)
			temp_task_c_h.append(c_h)
			temp_task_w_h.append(c_h/f_h)
			c_l = round(c_h*random.uniform(1.3,2.5), 1)
			temp_task_c_l.append(c_l)
			temp_task_w_l.append(round(c_l/f_l, 1))
		
		total_c_h = sum(temp_task_c_h)
		total_c_l = sum(temp_task_c_l)
		total_w_h = sum(temp_task_w_h)
		total_w_l = sum(temp_task_w_l)

		u = i/100.0
		scaling = u*d/total_c_l

		for task in range(tasks): # Normalizing c and w to fit utility
			task_c_h.append(temp_task_c_h[task]*scaling)
			task_c_l.append(temp_task_c_l[task]*scaling)
			task_w_h.append(temp_task_w_h[task]*scaling)
			task_w_l.append(temp_task_w_l[task]*scaling)
		for task in range(tasks): # Generating utility for each task
			temp_num = round(random.randint(1,10), 1)
			temp.append(temp_num)
			total = total + temp_num
		for util in temp: # Normalizing utility to sum to u
			u_tasks.append(util/total*u)
		for task in range(tasks): # a and alpha generation
			a_h.append(1.0)
			alpha_h.append(0.1)
			temp = random.randint(20, 50)/100
			a_l.append(temp)
			alpha_l.append(round(temp/10, 3))
		for task in range(tasks): # Power on HP and LP
		    power_h.append(round((a_h[task]*pow(f_h, 3)) + alpha_h[task], 1))
		    power_l.append(round((a_l[task]*pow(f_l, 3)) + alpha_l[task], 1))
		for task in range(tasks):
			levels.append("")
		for edge in edges: # Separating tasks into levels
			for level_index in range(len(levels)):
				if edge[0] in levels[level_index]:
					levels[level_index+1] = levels[level_index+1] + edge[5] + " "

		levels = list(filter(None, levels))

		for level_index in range(1, len(levels)):
			levels[level_index] = levels[level_index][:-1]

		time_l = task_w_l[0]
		time_h = task_w_l[0]
		time_l_array[0] = 0
		core_finish_time_each_task.append("L" + str(time_l))
		order.append(0)
		tasks_left = tasks - 1

		#LTF

		for task in levels[1].split(): # Storing time for each task in next_tasks
			next_tasks[task] = task_w_h[int(task)]
		next_tasks = {k: v for k, v in sorted(next_tasks.items(), key=lambda item: item[1], reverse=True)}

		while(tasks_left > 0): # Assigning tasks to HP and LP
			for task in list(next_tasks):
				order.append(int(task))
				if time_l <= time_h:
					time_l_array[task] = time_l
					time_l = time_l + next_tasks[task]
					l_total_time = l_total_time + next_tasks[task]
					core_finish_time_each_task.append("L" + str(time_l))
					power_l_total = power_l_total + power_l[int(task)]
					energy_total = energy_total + power_l[int(task)]*next_tasks[task]
					for edge in edges:
						if edge[0] == task:
							if edge[5] == ' ':
								temp_dict[edge[6:]] = task_c_h[int(edge[6:])]
							else:
								temp_dict[edge[5:]] = task_c_h[int(edge[5:])]
					tasks_left = tasks_left - 1
					del next_tasks[task]
					#print("L: ", task)
				else:
					time_h_array[task] = time_h
					time_h = time_h + next_tasks[task]
					h_total_time = h_total_time + next_tasks[task]
					core_finish_time_each_task.append("H" + str(time_h))
					power_h_total = power_h_total + power_h[int(task)]
					energy_total = energy_total + power_h[int(task)]*next_tasks[task]
					for edge in edges:
						if edge[0] == task:
							if edge[5] == ' ':
								temp_dict[edge[6:]] = task_c_h[int(edge[6:])]
							else:
								temp_dict[edge[5:]] = task_c_h[int(edge[5:])]
					tasks_left = tasks_left - 1
					del next_tasks[task]
					#print("H: ", task)
			if bool(next_tasks) == False or time_h > time_l:
				for t in list(temp_dict):
					next_tasks[t] = temp_dict[t]
				temp_dict = {}
				time_h = time_l

		ltf_power = power_h_total + power_l_total
		idle_l = d - l_total_time
		idle_h = d - h_total_time
		energy_total_ltf = energy_total + idle_h * 0.05 + idle_l * 0.02 
		average_energy_total_ltf = average_energy_total_ltf + energy_total_ltf

		#US

		temp = 0
		for task in order[::-1]: # Finds tightest task
			primary_contingency_finish[task] = 100 - temp
			backup_contingency_start[task] = primary_contingency_finish[task] - task_w_h[int(task)]
			temp = temp + task_w_l[int(task)]
			if task in time_l_array.keys():
				if (backup_contingency_start[task] - time_l_array[task]) < tightest_value and backup_contingency_start[task] > task_w_l[task]:
					tightest_value = backup_contingency_start[task] - time_l_array[task]
					tightest = int(task)

		ratio = task_w_l[tightest] / (tightest_value) 
		#print(ratio)
		#for task in order:
		#	print("Task " + str(task) + ": " + str(task_w_l[int(task)]))

		l_total_time = l_total_time * ratio
		idle_l = d - l_total_time
		h_total_time = h_total_time * ratio
		idle_h = d - h_total_time
		ltf_us_power = ltf_power * ratio

		energy_total_ltf_us = energy_total*ratio + idle_h * 0.05 + idle_l * 0.02
		average_energy_total_ltf_us = average_energy_total_ltf_us + energy_total_ltf_us
	
	graph_utilization_ltf.append(u*100)
	average_energy_total_ltf = average_energy_total_ltf/(upper_limit - lower_limit)
	average_energy_total_ltf_us = average_energy_total_ltf_us/(upper_limit - lower_limit)
	graph_power_ltf.append(average_energy_total_ltf)
	graph_power_ltf_us.append(average_energy_total_ltf_us)

x_ltf = graph_utilization_ltf
y_ltf = []
y_ltf_us = []

max_y_ltf = max(graph_power_ltf)
for i in graph_power_ltf:
	y_ltf.append(i/max_y_ltf * 100)

max_y_ltf_us = max(graph_power_ltf_us)
for i in graph_power_ltf_us:
	y_ltf_us.append(i/max_y_ltf_us * 100)

#print(x_ltf)
#print(y_ltf_us)

ltf = dict(zip(x_ltf, y_ltf))
ltf_us = dict(zip(x_ltf, y_ltf_us))

ltf = sorted(ltf.items())
x, y = zip(*ltf)
ltf_us = sorted(ltf_us.items())
x_us, y_us = zip(*ltf_us)

plt.plot(x, y, label = "LTF")
plt.plot(x_us, y_us, label = "LTF-US")
plt.xlabel('Utilization')
plt.ylabel('Energy Consumption') 
plt.title('Impact of Utilization')
plt.legend()
plt.show() 