function [data] = Newmark2D_NearFieldScanN5245A_tunes_demux_fcn(objg,speedmms,defZeroInXsteps,defZeroInYsteps,...
    xmin,xmax,ymin,ymax,dstep,NumFreqs,fstart,fstop,NumApMasks,IFBW,calfile,~)

%% enter savename, aperture masks, and display the settings for user
power=3;
% savename='Holog2D_pos_60';
savename='2D_Holography_Test_bg';
sParMeas='S21';

fprintf('THIS IS FROM THE 2DMA_Aaron DIRECTORY \n')

% load('D:\MATLAB\timager2d\masks\masksVarN.mat')
% load('D:\MATLAB\timager2d\masks\masksPan4.mat') %USE THIS FOR FULL SYSTEM
% load('D:\MATLAB\timager2d\masks\masksSubChunk3.mat')
load('C:\Users\LabFloor2\Dropbox (Duke Electric & Comp)\2DMA_Aaron\Mask_files\masksRandom_45on_1000.mat')
% load('C:\Users\LabFloor2\Dropbox (Duke Electric & Comp)\2DMA_Aaron\Mask_files\masks_Linearity_Test_2.mat')

ApMasks=masks.masksDe;

fprintf(['\nIFBW = %g\nCal = ',calfile,...
    '\nnumber of masks = %i \npower = %i dBm\nMeasuring ',...
    sParMeas,' by hard-coding\n'], IFBW, NumApMasks, power);

%% initialize instruments

fclose('all');
delete(instrfindall);

hware.vobj_switch = agilent_11713C_switchdriver_startVISAObject;
agilent_11713C_switchdriver_closeAll(hware.vobj_switch)

vobj_vna=InstrumentOpen('visa','agilent','N5245A');
[buffersize,f]=VNAInitiate(vobj_vna,...
    NumFreqs,...
    fstart,fstop,...
    IFBW,power,sParMeas,...
    calfile);

serPort = startSerial('COM5');


%HARDCODE TO ALLOW ONLY CHANNEL 2!!!!!!!!!!!!!!!!
agilent_11713C_switchdriver_closeAll(hware.vobj_switch)
pause(0.05)
agilent_11713C_switchdriver_openChannelNumbers(hware.vobj_switch,1,2)
pause(0.05)
agilent_11713C_switchdriver_openChannelNumbers(hware.vobj_switch,2,2)
pause(0.05)
    

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
pp=4; %HARDCODE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
