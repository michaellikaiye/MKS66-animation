import mdl
from display import *
from matrix import *
from draw import *
from os import mkdir, path

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    frames = basename = vary = False

    name = 'default'
    num_frames = 1

    for c in commands:
        if c['op'] == 'frames':
            num_frames = int(c['args'][0])
            frames = True
        if c['op'] == 'vary':
            vary = True
        if c['op'] == 'basename':
            name = c['args'][0]
            basename = True
    if vary and not frames:
        print 'vary found but frames not found'
        exit(1)
    if frames and not basename:
        print 'frames found but basename not found'
        print 'basename will be set to [default]'

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    for c in commands:
        if c['op'] == 'vary':
            initF, termF = int(c['args'][0]), int(c['args'][1])
            initV, termV = c['args'][2], c['args'][3]
            if termF <= initF or initF < 0 or termF >= num_frames:
                print 'error: bad start or end frame value'
            dV = (termV - initV) / (termF - initF)
            V = initV
            for i in range(initF, termF + 1):
                frames[i][c['knob']] = V
                V += dV

    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    if num_frames > 1:
        if not path.exists('anim/' + name):
            mkdir('anim/' + name)
    for i in range(num_frames):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        if num_frames > 1:
            for knob in frames[i]:
                symbols[knob][1] = frames[i][knob]

        for command in commands:
            print command
            c = command['op']
            args = command['args']
            v = 1
            if c == 'mesh':
                print('hoi')
                vets = []
                nors = []
                iz = -1
                gg = open(args[0], 'r')
                for line in gg.readlines():
                    words = line.split(' ')
                    if words[0] == 'g':
                        iz += 1
                        vets.append([None])
                        nors.append([None])
                    if words[0] == 'v':
                        vets[iz].append([float(words[1]), float(words[2]), float(words[3])])
                    if words[0] == 'vn':
                        nors[iz].append([float(words[1]), float(words[2]), float(words[3])])
                    if words[0] == 'f':
                        f = []
                        for j in range(1, len(words)):
                            if word[j].count('/') == 0:
                                f.append(vets[iz][int(word[j])])
                            else:
                                s = word[j].split('/')
                                f.append(vets[iz][int(s[0])])
                        if len(f) > 2:
                            polymon = []
                            for i in range(2, len(f)):
                                add_polygons(polymon, f[0][0],f[0][1],f[0][1],
                                                 f[1][0],f[1][1],f[1][2],
                                                 f[i][0],f[i][1],f[i][2])
                        draw_polygons(polymon, screen, zbuffer, view, ambient, light, symbols, reflect)
                    
                            
                        
            elif c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                if command['knob']:
                    v = symbols[command["knob"]][1]
                tmp = make_translate(args[0] * v, args[1] * v, args[2] * v)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if command['knob']:
                    v = symbols[command["knob"]][1]
                tmp = make_scale(args[0] * v, args[1] * v, args[2] * v)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if command['knob']:
                    v = symbols[command["knob"]][1]
                theta = args[1] * (math.pi/180) * v
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if num_frames > 1:
            filename = 'anim/' + name + '/' + name + ('%03d'%i)
            save_extension(screen, filename)

    if num_frames > 1:
        make_animation(name)
    print symbols
