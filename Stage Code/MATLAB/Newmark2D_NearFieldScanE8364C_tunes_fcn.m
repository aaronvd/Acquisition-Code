function [data] = Newmark2D_NearFieldScanE8364C_tunes_fcn(objg,speedmms,defZeroInXsteps,defZeroInYsteps,...
    xmin,xmax,ymin,ymax,dstep,NumFreqs,fstart,fstop,NumApMasks,IFBW,calfile,~)

%% enter savename, aperture masks, and display the settings for user
power=0;
savename='pr6';
sParMeas='S12';

fprintf('THIS IS FROM THE TIMAGER 2D DIRECTORY \n')

% load('D:\MATLAB\timager2d\masks\masksVarN.mat')
load('D:\MATLAB\timager2d\masks\masksPan4.mat') %USE THIS FOR FULL SYSTEM
% load('D:\MATLAB\timager2d\masks\masksSubChunk3.mat')

ApMasks=masks.masksDe;

fprintf(['\nIFBW = %g\nCal = ',calfile,...
    '\nnumber of masks = %i \npower = %i dBm\nMeasuring ',...
    sParMeas,' by hard-coding\n'], IFBW, NumApMasks, power);

%% initialize instruments
delete(instrfind)

vobj_vna=InstrumentOpen('visa','agilent','E8364C');
[buffersize,f]=VNAInitiate(vobj_vna,...
    NumFreqs,...
    fstart,fstop,...
    IFBW,power,sParMeas,...
    calfile);

serPort = startSerial('COM5');
% serPort = startSerial('COM6');

%% setup scan
[X, Y] = meshgrid(xmin:dstep:xmax,ymin:dstep:ymax);
measurements = zeros(size(Y,1),size(X,2),NumFreqs,NumApMasks);
stops = size(Y,1)*size(X,2);

%% begin scan!
tic
stopscomp=0;

for yn=1:size(Y,1)
    direction = 2*mod(yn,2)-1;
    if direction>0
        xindex = 1:size(X,2);
    else
        xindex = size(X,2):-1:1;
    end
    for xn=xindex
        x = X(yn,xn);
        y = Y(yn,xn);
        Newmark2D_stage_moveToAbsolute(objg,speedmms,defZeroInXsteps,defZeroInYsteps,x,y); %recomm. speed 25 mm/sec
        
        for jj=1:NumApMasks

% MULTI-PANEL          
pp=6; %HARDCODE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ApTemp=ApMasks(jj,:);
str_x = strcat(num2str(12),',',num2str(ApTemp),',',num2str(pp));
fprintf(serPort,str_x);

% % SINGLE PANEL
% ApTemp=ApMasks(jj,:);
% str_x = strcat(num2str(12),',',num2str(ApTemp));
% fprintf(serPort,str_x);

            pause(0.01)
            measurements(yn,xn,:,jj) = VNARead(vobj_vna,buffersize,sParMeas);
        end

        stopscomp = stopscomp+1;
        timere = (stops-stopscomp)*toc/3600;
        disp(['Est. time remaining: ' num2str(timere) ' hours'])
        tic
    end
    figure(2); imagesc(abs(measurements(:,:,round(length(measurements(1,1,:,1))/2),1)))
end


data.X = X;
data.Y = Y;
data.f = f;
data.masks=masks;
data.measurements = measurements;
a=clock;
save(['D:\NFS Default Directory\',...
    savename,'_',date,'_',num2str(a(4)),'_',num2str(a(5))],'data')

%% clean up communications
fprintf(vobj_vna,'DISP:ENABLE on');
InstrumentClose();
