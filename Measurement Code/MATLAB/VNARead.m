%+===================================================================+ +-------+
%| MetaImager                                    Duke University ECE | |       |
%|                                                                   | |       |
%| VNARead.m                                                         | |       |
%+===================================================================+ +-------+
% VNAREAD Trigger and record VNA measurement
%   [DATA]=VNAREAD(VNA,BUFFERSIZE,SPARAMETER)

function [data]=VNARead(vna,buffersize,s)
    % Set channel
    fprintf(vna,['CALC:PAR:SEL "Meas',s,'"']);
    query(vna,'*OPC?');
    % Trigger
    fprintf(vna,'INIT:IMM');
    query(vna,'*OPC?');
	% Read
    fprintf(vna,'CALC:FORM IMAG');
    fprintf(vna,'CALC:DATA? FDATA');
    simag=eval(['[',fscanf(vna,'%c',buffersize),']']);
    query(vna,'*OPC?');
    fprintf(vna,'CALC:FORM REAL');
    fprintf(vna,'CALC:DATA? FDATA');
    sreal=eval(['[',fscanf(vna,'%c',buffersize),']']);
    query(vna,'*OPC?');
	% Format
    data=sreal+1i.*simag;
end


