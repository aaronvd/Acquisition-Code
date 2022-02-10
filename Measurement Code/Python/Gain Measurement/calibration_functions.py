import numpy as np
import skrf as rf

def make_SOL_cal(filepath):
    
    SHORT_S11 = np.load(filepath + 'SHORT_S11.ntwk', allow_pickle = True)
    OPEN_S11 = np.load(filepath + 'OPEN_S11.ntwk', allow_pickle = True)
    LOAD_S11 = np.load(filepath + 'LOAD_S11.ntwk', allow_pickle = True)

    SHORT = SHORT_S11
    n_freq = len(SHORT.f)
    freq = rf.Frequency(SHORT.f[0], SHORT.f[-1], n_freq, 'hz')
    SHORT.z0 = (50+0j) * np.ones((n_freq, 4)) 

    OPEN = OPEN_S11
    OPEN.z0 = (50+0j) * np.ones((n_freq, 4)) 

    LOAD = LOAD_S11
    LOAD.z0 = (50+0j) * np.ones((n_freq, 4)) 

    my_measured = [\
                   SHORT,
                   OPEN,
                   LOAD
            ]
      
    # Ideal OPEN
    base_ntwk = rf.Freespace(freq, z0=50+0j)
    OPEN_S11_85521A = base_ntwk.delay_load(1, 31.832, unit = 'ps')
    OPEN_85521A = OPEN_S11_85521A
    OPEN_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    # Ideal SHORT
    SHORT_S11_85521A = base_ntwk.delay_load(-1, 30.581, unit = 'ps')
    SHORT_85521A = SHORT_S11_85521A
    SHORT_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    #Ideal LOAD
    LOAD_S11_85521A = base_ntwk.delay_load(0,0)
    LOAD_85521A = LOAD_S11_85521A
    LOAD_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    my_ideals = [\
        SHORT_85521A,
        OPEN_85521A,
        LOAD_85521A
                ]
    
    cal = rf.OnePort(\
        ideals = my_ideals,
        measured = my_measured,
        )
    
    cal.run()
    
    return cal

def make_SOLT_cal(filepath):
    
    SHORT_S11 = np.load(filepath + 'SHORT_S11.ntwk', allow_pickle = True)
    SHORT_S22 = np.load(filepath + 'SHORT_S22.ntwk', allow_pickle = True)
    OPEN_S11 = np.load(filepath + 'OPEN_S11.ntwk', allow_pickle = True)
    OPEN_S22 = np.load(filepath + 'OPEN_S22.ntwk', allow_pickle = True)
    LOAD_S11 = np.load(filepath + 'LOAD_S11.ntwk', allow_pickle = True)
    LOAD_S22 = np.load(filepath + 'LOAD_S22.ntwk', allow_pickle = True)
    THRU_S11 = np.load(filepath + 'THRU_S11.ntwk', allow_pickle = True)
    THRU_S22 = np.load(filepath + 'THRU_S22.ntwk', allow_pickle = True)
    THRU_S21 = np.load(filepath + 'THRU_S21.ntwk', allow_pickle = True)
    THRU_S12 = np.load(filepath + 'THRU_S12.ntwk', allow_pickle = True)

    SHORT = rf.two_port_reflect(SHORT_S11,SHORT_S22)
    n_freq = len(SHORT.f)
    freq = rf.Frequency(SHORT.f[0], SHORT.f[-1], n_freq, 'hz')
    
    SHORT.z0 = (50+0j) * np.ones((n_freq, 4)) 

    OPEN = rf.two_port_reflect(OPEN_S11,OPEN_S22)
    OPEN.z0 = (50+0j) * np.ones((n_freq, 4)) 

    LOAD = rf.two_port_reflect(LOAD_S11,LOAD_S22)
    LOAD.z0 = (50+0j) * np.ones((n_freq, 4)) 

    THRU = rf.two_port_reflect(THRU_S11, THRU_S22)
    THRU.s[:,0,1] = THRU_S12.s[:,0,0]
    THRU.s[:,1,0] = THRU_S21.s[:,0,0]
    THRU.z0 = (50+0j) * np.ones((n_freq, 4)) 

    my_measured = [\
                   SHORT,
                   OPEN,
                   LOAD,
                   THRU
            ]
    
    # Ideal THRU
    base_ntwk = rf.Freespace(freq, z0=50+0j)
    THRU_85521A = base_ntwk.line(115.881,unit ='ps')
    THRU_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    # Ideal OPEN
    OPEN_S11_85521A = base_ntwk.delay_load(1, 31.832, unit = 'ps')
    OPEN_S22_85521A = OPEN_S11_85521A 
    OPEN_85521A = rf.two_port_reflect(OPEN_S11_85521A, OPEN_S22_85521A)
    OPEN_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    # Ideal SHORT
    SHORT_S11_85521A = base_ntwk.delay_load(-1, 30.581, unit = 'ps')
    SHORT_S22_85521A = SHORT_S11_85521A
    SHORT_85521A = rf.two_port_reflect(SHORT_S11_85521A,SHORT_S22_85521A)
    SHORT_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    #Ideal LOAD
    LOAD_S11_85521A = base_ntwk.delay_load(0,0)
    LOAD_85521A = rf.two_port_reflect(LOAD_S11_85521A)
    LOAD_85521A.z0 = (50+0j) * np.ones((n_freq, 4)) 
    
    my_ideals = [\
        SHORT_85521A,
        OPEN_85521A,
        LOAD_85521A,
        THRU_85521A,
        ]
    
    cal = rf.TwelveTerm(\
        ideals = my_ideals,
        measured = my_measured,
        )
    
    cal.run()
    
    return cal


def make_TRL_cal(filepath):
        
    THRU_S11 = np.load(filepath + 'THRU_S11.ntwk', allow_pickle = True)
    THRU_S22 = np.load(filepath + 'THRU_S22.ntwk', allow_pickle = True)
    THRU_S21 = np.load(filepath + 'THRU_S21.ntwk', allow_pickle = True)
    THRU_S12 = np.load(filepath + 'THRU_S12.ntwk', allow_pickle = True)
    REFLECT_S11 = np.load(filepath + 'REFLECT_S11.ntwk', allow_pickle = True)
    REFLECT_S22 = np.load(filepath + 'REFLECT_S22.ntwk', allow_pickle = True)
    REFLECT_S21 = np.load(filepath + 'REFLECT_S21.ntwk', allow_pickle = True)
    REFLECT_S12 = np.load(filepath + 'REFLECT_S12.ntwk', allow_pickle = True)
    LINE_S11 = np.load(filepath + 'LINE_S11.ntwk', allow_pickle = True)
    LINE_S22 = np.load(filepath + 'LINE_S22.ntwk', allow_pickle = True)
    LINE_S21 = np.load(filepath + 'LINE_S21.ntwk', allow_pickle = True)
    LINE_S12 = np.load(filepath + 'LINE_S12.ntwk', allow_pickle = True)
    SWITCH_TERMS = np.load(filepath + 'SWITCH_TERMS.ntwk', allow_pickle = True)
    
    THRU = rf.two_port_reflect(THRU_S11, THRU_S22)
    n_freq = len(THRU.f)
    pad_zeros = np.zeros((n_freq, 2, 2)) 
    THRU.s[:,0,1] = THRU_S12.s[:,0,0]
    THRU.s[:,1,0] = THRU_S21.s[:,0,0]
    THRU.z0  = (50+0j)*np.ones((n_freq, 4)) 
    
    REFLECT = rf.two_port_reflect(REFLECT_S11, REFLECT_S22)
    REFLECT.s[:,0,1] = REFLECT_S12.s[:,0,0]
    REFLECT.s[:,1,0] = REFLECT_S21.s[:,0,0]
    REFLECT.z0 = (50+0j)*np.ones((n_freq, 4))

    LINE = rf.two_port_reflect(LINE_S11, LINE_S22)
    LINE.s[:,0,1] = LINE_S12.s[:,0,0]
    LINE.s[:,1,0] = LINE_S21.s[:,0,0]
    LINE.z0 = (50+0j)*np.ones((n_freq, 4))
    
    my_ideals = [None, -1, None]

    my_measured = [THRU, REFLECT, LINE]

    cal = rf.TRL(\
        measured = my_measured,
        ideals = my_ideals,
        estimate_line = True,
        switch_terms = SWITCH_TERMS,
        )
    
    cal.run()
    
    return cal

















