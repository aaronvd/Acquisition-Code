%+===================================================================+ +-------+
%| MetaImager                                    Duke University ECE | |       |
%|                                                                   | |       |
%| VNAInitiate.m                                                     | |       |
%+===================================================================+ +-------+
% VNAINITIATE Initiates Agilent Vector Network Analyzer
%   [BUFFER,SWEEP]=VNAINITIATE(VNA,POINTS,F0,FN,IFBAND,POWER) initiates
%   Vector Network Analyzer object OBJECT

function [buffer,f]=VNAInitiate(vna,points,f0,fn,ifband,power,s,calfile)
    fprintf('Initiating VNA...');
    % Reset
    fprintf(vna,'SYST:PRES');

    % Set display
%     fprintf(vna,'DISP:ENAB OFF');
    fprintf(vna,'DISP:ENAB ON');
    % Set measurement
    fprintf(vna,['CALC:PAR:DEF:EXT "Meas',s,'",',s]);
    % Set calibration
    if exist('calfile','var')
        fprintf(vna,['SENS:CORR:CSET:ACT "',calfile,'",1']);
    end
    % Set power
    fprintf(vna,'SOUR:POW1 %s',num2str(power));
	% Set frequency
    fprintf(vna,['SENS:FREQ:STAR ',num2str(f0),'ghz']);
    fprintf(vna,['SENS:FREQ:STOP ',num2str(fn),'ghz']);
    % Set sweep
    fprintf(vna,['SENS:SWE:POIN ',num2str(points)]);
    % Set IF bandwidth
    fprintf(vna,['SENS:BAND ',num2str(ifband)]);
    % Set trigger
    fprintf(vna,'INIT:CONT OFF');
    fprintf(vna,'TRIG:SOUR MAN');
    fprintf(vna,'TRIG:SCOP CURR');
    % Set output
    fprintf(vna,'FORM:DATA ASCII,0');
    % Set buffer
    buffer=points*20; % N5245A output strings are 20 characters
    fclose(vna);
    set(vna,'InputBufferSize',buffer);
    fopen(vna);
    % Get sweep
    fprintf(vna,'SENS:X?');
    f=eval(['[',fscanf(vna,'%c',buffer),']']);
	% Synchronize
    query(vna,'*OPC?');
    fprintf('[Done]\n');
end
