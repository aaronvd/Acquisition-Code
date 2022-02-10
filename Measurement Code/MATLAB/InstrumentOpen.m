%+===================================================================+ +-------+
%| MetaImager                                    Duke University ECE | |       |
%|                                                                   | |       |
%| InstrumentOpen.m                                                  | |       |
%+===================================================================+ +-------+
% INSTRUMENTOPEN Establish instrument connection
%   [OBJ]=INSTRUMENTOPEN(INTERFACE,ADAPTOR,NAME) searches for and connects to
%   the specified INTERFACE ADAPTOR NAME, returning an instrument object OBJ.

% Note: The magic instrument ID for Agilent VNA is hpic7,16

function [object]=InstrumentOpen(interface,adaptor,name)
    fprintf('Opening %s... ',name);
    % Enumerate instruments
    available=instrhwinfo(interface,adaptor);
    active=instrfind();
    % Search
    for i=1:length(available.ObjectConstructorName)
		% Get object
        found=0;
        for j=1:length(active)
            if strfind(available.ObjectConstructorName{i},active(j).RsrcName)
                found=j;
				break
            end
        end
        if found
            object=active(j);
        else
            object=eval(available.ObjectConstructorName{i});
        end
		closed=strcmp(object.Status,'closed');
        if closed
            fopen(object);
        end
		% Identify
		fprintf(object,'*IDN?');
        % Hit
        if strfind(fscanf(object),name)
            fprintf('[Done]\n');
            return
        end
		% Miss
        if closed
		    fclose(object);
        end
		if ~found
			delete(object);
		end
    end
	% Not found
    fprintf(2,'[Fail]\n');
end
