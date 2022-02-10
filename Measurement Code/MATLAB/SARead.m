%+===================================================================+ +-------+
%| Aaron Diebold                                 Duke University ECE | |       |
%|                                                                   | |       |
%| SARead.m                                                         | |       |
%+===================================================================+ +-------+
% SARead Trigger and record SA measurement
%   [DATA]=SARead(SA,BUFFERSIZE)

function [data]=SARead(sa)
    % Trigger
    fprintf(sa,'INIT:IMM');
    query(sa,'*OPC?');
	% Read
    % Get sweep
    fprintf(sa,'TRAC? TRACe1');
    data = eval(['[',fscanf(sa,'%c'),']']);
    query(sa,'*OPC?');
end


