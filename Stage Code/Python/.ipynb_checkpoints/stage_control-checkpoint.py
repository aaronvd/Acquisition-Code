def stage_start(address):
    g = gclib.py()
    g.GOpen(address)
    print(g.GInfo())
    return g

def zero_axes(g):
    defZeroInXsteps = float(g.GCommand('MG _RPA'))
    defZeroInYsteps = float(g.GCommand('MG _RPB'))
    return defZeroInXsteps, defZeroInYsteps

def stage_home(g,speedmms):
    steptomm = 5000
    stepperspeed = np.round(speedmms*steptomm)
    stepperaccel = np.round(10*stepperspeed)
    
    program = ('#HOME;' +
                'AC {},{};'.format(stepperaccel, stepperaccel) +
                'DC {},{};'.format(stepperaccel, stepperaccel) +
                'JG {},{};'.format(-stepperspeed, -stepperspeed) +
                'NOTE jog until you hit limits;' +
                'BG;' +
                'NOTE wait for end of move;' +
                'AM;'+
                'NOTE take 1mm step back from edge;' +
                'PR 10000,10000;' +
                'BG;' +
                'AM;' +
                'DP 0,0;' +
                'NOTE capture min,max step val;' +
                'minx=_RPA;' +
                'miny=_RPB;' +
                'NOTE jog to other side and record pos;' +
                'SP 125000,125000;' +
                'EN;')
    g.GProgramDownload(program, '')
    g.GCommand('XQ')
    
    xminstepVal = float(g.GCommand('MG minx'))
    yminstepVal = float(g.GCommand('MG miny'))
    
    return xminstepVal, yminstepVal

def move_to_relative(g,speedmms,defZeroInXsteps,defZeroInYsteps,moveXmm,moveYmm):
    steptomm = 5000
    stepperspeed = np.round(speedmms*steptomm)
    stepperaccel = np.round(10*stepperspeed)
    
    print(moveXmm)
    print(moveYmm)

    program = ('#MOVEREL;' +
                'AC {},{};'.format(stepperaccel, stepperaccel) +
                'DC {},{};'.format(stepperaccel, stepperaccel) +
                'SP {},{};'.format(stepperspeed, stepperspeed) +
                'NOTE move relative position;' +
                'PR {},{};'.format(-moveXmm*steptomm,-moveYmm*steptomm) +
                'BG;' +
                'NOTE wait for end of move;'+
                'AM;'+
                'posx=_RPA'+
                'posy=_RPB'+
                'EN;')
    g.GProgramDownload(program, '')
    g.GCommand('XQ')
    
    xposSteps = float(g.GCommand('MG posx'))
    yposSteps = float(g.GCommand('MG posy'))
    
    xUserPos = -(xposSteps-defZeroInXsteps)/steptomm;
    yUserPos = -(yposSteps-defZeroInYsteps)/steptomm;
    
    return xUserPos, yUserPos

def move_to_absolute(g,speedmms,defZeroInXsteps,defZeroInYsteps,moveToUserXmm,moveToUserYmm):
    steptomm = 5000
    stepperspeed = np.round(speedmms*steptomm)
    stepperaccel = np.round(10*stepperspeed)
    
    program = ('#MOVEABS;' +
                'AC {},{};'.format(stepperaccel, stepperaccel) +
                'DC {},{};'.format(stepperaccel, stepperaccel) +
                'SP {},{};'.format(stepperspeed, stepperspeed) +
                'NOTE move to abs position;' +
                'PA {},{};'.format(-moveToUserXmm*steptomm+defZeroInXsteps,-moveToUserYmm*steptomm+defZeroInYsteps) +
                'BG;' +
                'NOTE wait for end of move;'+
                'AM;'+
                'posx=_RPA'+
                'posy=_RPB'+
                'EN;')
    g.GProgramDownload(program, '')
    g.GCommand('XQ')
    
    xpos = float(g.GCommand('MG posx'))
    ypos = float(g.GCommand('MG posy'))
    
    xUserPos = -(xpos-defZeroInXsteps)/steptomm;
    yUserPos = -(ypos-defZeroInYsteps)/steptomm;
    
    return xUserPos, yUserPos

def close_connection(g):
    g.GClose()
























