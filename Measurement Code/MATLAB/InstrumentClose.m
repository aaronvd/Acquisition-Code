%+===================================================================+ +-------+
%| MetaImager                                    Duke University ECE | |       |
%|                                                                   | |       |
%| InstrumentClose.m                                                 | |       |
%+===================================================================+ +-------+
% INSTRUMENTCLOSE Close instrument connections
%   INSTRUMENTCLOSE() closes all connected instruments

function InstrumentClose()
    delete(instrfind());
end
