%+===================================================================+ +-------+
%| Aaron Diebold                                 Duke University ECE | |       |
%|                                                                   | |       |
%| SAInitiate.m                                                     | |       |
%+===================================================================+ +-------+
% SAINITIATE Initiates Agilent Spectrum Analyzer
%   [BUFFER,SWEEP]=SAINITIATE(SA,POINTS,F0,FN,IFBAND,POWER) initiates
%   Spectrum Analyzer object SA

function [f_start, f_stop, buffer]=SAInitiate(sa,f0,fn,avg_number,sweep_time)
    fprintf('Initiating SA...');
    % Reset
    fprintf(sa,'SYST:PRES');
    fprintf(sa,'*CLS');
    fprintf(sa,'*RST');
    % Detection type
    fprintf(sa,'SENS:DET:TRACe1:FUNC POS');
    % Power settings
%     fprintf(sa,'UNIT:POW DBM'); % Set Y-Axis units to volts
    fprintf(sa,'SENS:POW:RF:GAIN:STAT ON'); % RF Preamp
    fprintf(sa,'SENS:POW:RF:ATT 0'); % Attenuation (dB)
%     fprintf(sa,'SENS:POW:RF:HSEN:STAT ON'); %High-Sensitivity Mode
	% Set frequency
    fprintf(sa,['SENS:FREQ:STAR ',num2str(f0),'ghz']);
    fprintf(sa,['SENS:FREQ:STOP ',num2str(fn),'ghz']);
    fprintf(sa, 'SENS:FREQ:STAR?');
    f_start = eval(['[',fscanf(sa,'%c'),']']);
    fprintf(sa, 'SENS:FREQ:STOP?');
    f_stop = eval(['[',fscanf(sa,'%c'),']']);
    % Set sweep
    fprintf(sa,['SENS:BAND:RES ',num2str(3),'mhz']); %Resolution BW
    fprintf(sa,'SENS:BAND:VID:AUTO ON'); % Couples VBW to RBW
    fprintf(sa,'SENS:SWE:SPE NORM'); % Swept mode
    fprintf(sa,['SENS:SWE:TIME ',num2str(sweep_time)]);
%     fprintf(sa,'SENS:SWE:SPE FAST');   % FFT mode
    % Set averaging
    fprintf(sa,['SENS:AVER:TRAC:COUN ',num2str(avg_number)]); % # averages
    % Set trigger
    fprintf(sa,'INIT:CONT OFF');
    % Set output data type
    fprintf(sa,'FORM:TRAC ASCii');
    % Set buffer
%     buffer=points*20; % N5245A output strings are 20 characters
    buffer = 10E6;
    fclose(sa);
    set(sa,'InputBufferSize',buffer);
    fopen(sa);
	% Synchronize
    query(sa,'*OPC?');
    fprintf('[Done]\n');
end
