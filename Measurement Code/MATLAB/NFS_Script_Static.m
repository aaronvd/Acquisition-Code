clear

c = 3e8;
xrange = 1000; % x length of stage, mm
yrange = 1000; % y length of stage, mm

%% scan parameters
fstart = 8;
fstop = 12;
NumFreqs = 401;
lam_max = c/(fstop*1e9);
dstep = lam_max/2 * 1000; % mm

IFBW = 1000;
calfile = 'Aaron_green_cables_21-10-22';
power=0;
savename='X_Band_Horn';
sParMeas='S12';
speedmms = 25;

fprintf(['\nIFBW = %g\nCal = ',calfile,...
    '\npower = %i dBm\nMeasuring ',...
    sParMeas, '\n'], IFBW, power);

%% set scan lengths
Lx_ap = 130;
Ly_ap = 120;
theta = 60;
d = 80;

Lx_scan = Lx_ap + 2*d*tan(theta*pi/180);
Ly_scan = Ly_ap + 2*d*tan(theta*pi/180);

xmin = -Lx_scan/2;
xmax = Lx_scan/2;
ymin = -Ly_scan/2;
ymax = Ly_scan/2;

%% initialize instruments
delete(instrfind)

% VNA
vobj_vna=InstrumentOpen('visa','agilent','N5224A');     
[buffersize,f]=VNAInitiate(vobj_vna,...
    NumFreqs,...
    fstart,fstop,...
    IFBW,power,sParMeas,...
    calfile);

% Stage
objg = Newmark2D_stage_start();

%% move to new origin
center_x = -xrange/2;
center_y = -yrange/2;
pos_x = 0;  % adjust to change x zero position
pos_y = 0;  % adjust to change y zero position

Newmark2D_stage_moveToAbsolute(objg,speedmms,0,0,center_x+pos_x,center_y+pos_y)

%% zero axes
[defZeroInXsteps, defZeroInYsteps] = Newmark2D_stage_zeroAxes(objg);

%% setup scan
[X, Y] = meshgrid(xmin:dstep:xmax, ymin:dstep:ymax);
measurements = zeros(size(Y,1), size(X,2), NumFreqs);
stops = size(Y,1) * size(X,2);

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
      
            measurements(yn,xn,:,jj) = VNARead(vobj_vna,buffersize,sParMeas);

            stopscomp = stopscomp+1;
            timere = (stops-stopscomp)*toc/3600;
            disp(['Est. time remaining: ' num2str(timere) ' hours'])
            tic
            figure(2); imagesc(abs(measurements(:,:,round(size(measurements, 3)/2))))
        end
end


data.X = X;
data.Y = Y;
data.f = f;
data.measurements = measurements;
a=clock;
save(['C:\Users\smithlab\Documents\Near_Field_Scans\',...           
    savename,'_',date,'_',num2str(a(4)),'_',num2str(a(5))],'data')

%% clean up communications
fprintf(vobj_vna,'DISP:ENABLE on');
InstrumentClose();
Newmark2D_stage_stop(objg)





