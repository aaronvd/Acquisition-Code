close all
clc

% Load structure containing tuning states
filename = 'wrc_tuning_states.mat';
data = load(filename);

% Establish serial communication with Arduino
% Change 'COM3' to appropriate COM port, found under Device Manager
a = serial('COM3');
a.BaudRate = 115200;
fopen(a);

% Set tuning state. Look at data.ts_notes for descriptions of beams.
ind = 1;
metasurface_set(a, data.ts(:,:,ind));