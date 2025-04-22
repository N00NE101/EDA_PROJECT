#https://chatgpt.com/c/67f41c51-5184-8006-888b-4935a3b0f497
import random
from collections import defaultdict
locked = set()
def read_hypergraph(filename):
    with open(filename, 'r') as file:
        # Read the first line and extract n (vertices) and m (hyperedges)
        first_line = file.readline().strip()
        m, n = map(int, first_line.split())
        
        # Read each of the next m lines as a list of integers (hyperedges)
        hyperedges = []
        for _ in range(n):
            line = file.readline().strip()
            if line:  # Skip empty lines
                edge = list(map(int, line.split()))
                hyperedges.append(edge)

    return m, n, hyperedges

# Example usage
filename = 'hypergraph.txt'  # Replace with your file path
#m, n, hyperedges = read_hypergraph('bibd_49_3.mtx.hgr')
#m, n, hyperedges = read_hypergraph('Pd_rhs.mtx.hgr')
#m, n, hyperedges = read_hypergraph('test.hgr')
#m, n, hyperedges = read_hypergraph('gemat1.mtx.hgr')
m, n, hyperedges = read_hypergraph('ibm01.hgr')
print(f"Number of vertices: {n}")
print(f"Number of hyperedges: {m}")
print("Hyperedges:")
#for edge in hyperedges:
    #print(edge)

max_partition_size = (n/2) + 1
vertices = list(range(1,n+1))
random.shuffle(vertices)
mid = len(vertices) // 2
partition_A = set(vertices[:mid])
partition_B = set(vertices[mid:])
#partition_A = {1,2,3,4}
#partition_B = {5,6,7,8}
print("Partition A:", partition_A)
print("Partition B:", partition_B)
vertex_to_edges = defaultdict(list)
for edge_index, edge in enumerate(hyperedges):
    for vertex in edge:
        vertex_to_edges[vertex].append(edge_index)




edge_partition_counts = {}
for edge_idx, edge in enumerate(hyperedges):
        count = {'A': 0, 'B': 0}
        for vertex in edge:
            side = 'A' if vertex in partition_A else 'B'
            count[side] += 1
        edge_partition_counts[edge_idx] = count
gain_buckets = defaultdict(set)
vertex_gain = {}

for vertex in vertices:
    gain = 0
    current_partition = 'A' if vertex in partition_A else 'B'
    opposite_partition = 'B' if current_partition == 'A' else 'A'
    
    for edge_idx in vertex_to_edges[vertex]:
        counts = edge_partition_counts[edge_idx]
        
        if counts[current_partition] == 1:
            # This vertex is the only one on its side → would UNcut if moved
            gain += 1
        if counts[opposite_partition] == 0:
            # All other vertices are on current side → would CUT if moved
            gain -= 1

    vertex_gain[vertex] = gain
    gain_buckets[gain].add(vertex)

test = n
cut_edges = 0
prev_cut_edges = float('inf')
total_gain = 0
best_total_gain = float('-inf')
last_cycle_best_total_gain = 0
new_cycle = False
cycle_count = 0
exploration_counter = 20

move_sequence = []  # (vertex, from_partition)
best_gain_index = -1
original_partition_A = partition_A.copy()
original_partition_B = partition_B.copy()

while (test != 0): #BEGIN THE WHILE LOOP <----------------------------------------!!!!!
    if new_cycle:
        new_cycle = False
        edge_partition_counts = {}
        for edge_idx, edge in enumerate(hyperedges):
            count = {'A': 0, 'B': 0}
            for vertex in edge:
                side = 'A' if vertex in partition_A else 'B'
                count[side] += 1
            edge_partition_counts[edge_idx] = count
        gain_buckets = defaultdict(set)
        vertex_gain = {}

        for vertex in vertices:
            
            gain = 0
            current_partition = 'A' if vertex in partition_A else 'B'
            opposite_partition = 'B' if current_partition == 'A' else 'A'
            
            for edge_idx in vertex_to_edges[vertex]:
                counts = edge_partition_counts[edge_idx]
                
                if counts[current_partition] == 1:
                    # This vertex is the only one on its side → would UNcut if moved
                    gain += 1
                if counts[opposite_partition] == 0:
                    # All other vertices are on current side → would CUT if moved
                    gain -= 1
        
            vertex_gain[vertex] = gain
            gain_buckets[gain].add(vertex)
            #print(gain_buckets)

    randomlist = []
    best_gain = 0
    sorted_gain_buckets = sorted(gain_buckets.items(), reverse=True)
    if len(partition_A) > len(partition_B): #Choose Vertex from A
        found = False
        for gain, gain_vertices in sorted_gain_buckets:
            for vertex in gain_vertices:
                #print("GAIN VERTS",gain_vertices)
                if vertex in partition_A:
                    best_gain = gain
                    randomlist.append(vertex)
                    #print(randomlist)
                    found = True
            if found:
                break    
        best_vertex = random.choice(randomlist) #Randomly choose from the best (solves loop issues)
        #print(best_vertex)
        gain_buckets[best_gain].remove(best_vertex)
        if not gain_buckets[gain]:
            del gain_buckets[gain]
        randomlist.clear()        
        #if found:
            #break
    elif len(partition_A) < len(partition_B): #Choose Vertex from B
        found = False
        for gain, gain_vertices in sorted_gain_buckets:
            for vertex in gain_vertices:
                #print("GAIN VERTS",gain_vertices)
                if vertex in partition_B:
                    best_gain = gain
                    randomlist.append(vertex)
                    #print(randomlist)
                    found = True
            if found:
                break    
        best_vertex = random.choice(randomlist) #Randomly choose from the best (solves loop issues)
        #print(best_vertex)
        gain_buckets[best_gain].remove(best_vertex)
        if not gain_buckets[gain]:
            del gain_buckets[gain]
        randomlist.clear()        

    else:   #chooce vertex from either
        max_gain = max(gain_buckets.keys())
        best_vertex = next(iter(gain_buckets[max_gain]))
        gain_buckets[max_gain].remove(best_vertex)
        best_gain = max_gain
        if not gain_buckets[max_gain]:
            del gain_buckets[max_gain]

    total_gain = total_gain + best_gain
    if best_vertex in partition_A:
            from_partition, to_partition = 'A', 'B'
            partition_A.remove(best_vertex)
            partition_B.add(best_vertex)
    else:
        from_partition, to_partition = 'B', 'A'
        partition_B.remove(best_vertex)
        partition_A.add(best_vertex)
    locked.add(best_vertex)

    move_sequence.append((best_vertex, from_partition))
    for edge_idx in vertex_to_edges[best_vertex]: #update number of edges in partition 
            edge_partition_counts[edge_idx][from_partition] -= 1
            edge_partition_counts[edge_idx][to_partition] += 1


    for edge_idx in vertex_to_edges[best_vertex]: #Update neighbors gain
        for neighbor in hyperedges[edge_idx]:
            if neighbor in locked or neighbor == best_vertex:
                continue
 
            old_gain = vertex_gain[neighbor]

            if neighbor in gain_buckets[old_gain]:
                gain_buckets[old_gain].remove(neighbor)
            if not gain_buckets[old_gain]:
                del gain_buckets[old_gain]

            new_gain = 0 
            current_partition = 'A' if neighbor in partition_A else 'B'
            opposite_partition = 'B' if current_partition == 'A' else 'A'

            for e_idx in vertex_to_edges[neighbor]:
                counts = edge_partition_counts[e_idx]
                if counts[current_partition] == 1:
                    new_gain += 1
                if counts[opposite_partition] == 0:
                    new_gain -= 1
            
            vertex_gain[neighbor] = new_gain
            gain_buckets[new_gain].add(neighbor)
    test = test - 1
    if total_gain > best_total_gain:
            best_total_gain = total_gain

            best_cut_edges = cut_edges
            best_total_gain = total_gain
            best_gain_index = len(move_sequence)
    elif total_gain == best_total_gain and ((n % 2 == 0 and len(partition_A) == len(partition_B))):
            best_total_gain = total_gain

            best_cut_edges = cut_edges
            best_total_gain = total_gain
            best_gain_index = len(move_sequence)
            

      
    if test == 0 and best_total_gain > last_cycle_best_total_gain: # New cycle with better gain
        last_cycle_best_total_gain = best_total_gain
        total_gain = best_total_gain
        test = n
        locked.clear()
        print("NEW CYCLE!!!!!!!!!!!!!!!!!") #Debug 
        cycle_count = cycle_count + 1
        new_cycle = True
        print("LAST CYCLES BEST GAIN",last_cycle_best_total_gain) #debug
        print("NEW TOTAL GAIN", total_gain) #debug

        
    elif test == 0 and ((n % 2 == 0 and len(partition_A) != len(partition_B)) or (n % 2 != 0 and abs(len(partition_A) - len(partition_B)) >= 2)): #If not better gain, better split? 50-50?
        last_cycle_best_total_gain = best_total_gain
        total_gain = best_total_gain
        test = n
        locked.clear()
        print("NEW CYCLE!!!!!!!!!!!!!!!!!")
        cycle_count = cycle_count + 1
        new_cycle = True
        print("LAST CYCLES BEST GAIN",last_cycle_best_total_gain)
        print("NEW TOTAL GAIN", total_gain)

    
    elif test == 0: #Explore a little if convergining (just in case)
        if exploration_counter > 0:
            exploration_counter = exploration_counter - 1
            last_cycle_best_total_gain = best_total_gain
            total_gain = best_total_gain
            test = n
            locked.clear()
            print("NEW CYCLE!!!!!!!!!!!!!!!!!")
            cycle_count = cycle_count + 1
            new_cycle = True
            print("LAST CYCLES BEST GAIN",last_cycle_best_total_gain)
            print("NEW TOTAL GAIN", total_gain)

    if cycle_count >= 200: #ends the processes if taking too long
        break

    if new_cycle == True: #Reset for next cycle (using new info)
        Test_partition_A, Test_partition_B = original_partition_A.copy(), original_partition_B.copy()
        for i in range(best_gain_index):
            vertex, from_part = move_sequence[i]
            if from_part == 'A':
                Test_partition_A.remove(vertex)
                Test_partition_B.add(vertex)
            else:
                Test_partition_B.remove(vertex)
                Test_partition_A.add(vertex)
        original_partition_A, original_partition_B = Test_partition_A.copy(), Test_partition_B.copy() 
        partition_A = Test_partition_A.copy()
        partition_B = Test_partition_B.copy()  
        best_gain_index = 0
        move_sequence.clear()




print(f"Number of  cut edges: {cut_edges}")
#print("Vertex Gain", vertex_gain) #Too much info on large datasets
#print("Gain Buckets", gain_buckets) #Too much info on large datasets
#print("Partition A", partition_A) #Too much info on large datasets
#print("Partition B" , partition_B) #Too much info on large datasets

#print("Partition A", original_partition_A) #Too much info on large datasets
#print("Partition B" , original_partition_B) #Too much info on large datasets
#print("MOPVES", move_sequence) #Too much info on large datasets

cut_edges = 0 
for edge in hyperedges: #Calcuate number of edges cut
    in_A = any(v in original_partition_A for v in edge)
    in_B = any(v in original_partition_B for v in edge)        
    if in_A and in_B:
        cut_edges += 1

print("cut edges", cut_edges)