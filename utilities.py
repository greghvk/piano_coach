import pygame

notes = \
{
0: "C",
1: "C#",
2: "D",
3: "D#",
4: "E",
5: "F",
6: "F#",
7: "G",
8: "G#",
9: "A",
10: "A#",
11: "B"
}
def translateToNote(num):
    move = int(num/12) - 1
    note = notes[num%12]
    return note + str(move)

def print_devices():
    for n in range(pygame.midi.get_count()):
        print (n,pygame.midi.get_device_info(n))

def parse_to_list(track):
    x = [[msg.note, msg.velocity, msg.time] for msg in track if msg.type == 'note_on']
    for i in range(1, len(x)):
        x[i][2] += x[i-1][2]
    x = [msg for msg in x if msg[1]]
    
    final_list = [[[x[0][0]], x[0][2], int(x[0][2]/1920)]]
    for msg in x[1:]:
        if msg[2] == final_list[-1][1]:
            final_list[-1][0].append(msg[0])
        else:
            final_list.append([[msg[0]], msg[2], int(msg[2]/1920)])
    return final_list


def merge(t1, t2):
    merged = []
    cur_time = 0
    t1_idx = 0
    t2_idx = 0
    while t1_idx < len(t1) or t2_idx < len(t2):
        
        while t1_idx < len(t1) and (t2_idx == len(t2) or t1[t1_idx][1] < t2[t2_idx][1]):
            merged.append(t1[t1_idx])
            t1_idx += 1
            
        while t2_idx < len(t2) and (t1_idx == len(t1) or t2[t2_idx][1] < t1[t1_idx][1]):
            merged.append(t2[t2_idx])
            t2_idx += 1
            
        if t1_idx < len(t1) and t2_idx < len(t2) and t1[t1_idx][1] == t2[t2_idx][1]:
            merged.append(t1[t1_idx])
            t1_idx += 1
            for note in t2[t2_idx][0]:
                if note not in merged[-1][0]:
                    merged[-1][0].append(note)
            t2_idx += 1

    return merged
