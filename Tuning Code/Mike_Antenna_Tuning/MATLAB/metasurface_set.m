function metasurface_set(a,tuning_state)

dac=[    1  1  2  2  3  3 4 4 5 5 6 6 ;
         1  1  2  2  3  3 4 4 5 5 6 6 ;
         1  1  2  2  3  3 4 4 5 5 6 6 ;
         1  1  2  2  3  3 4 4 5 5 6 6 ;
        12 12 11 11 10 10 9 9 8 8 7 7 ;
        12 12 11 11 10 10 9 9 8 8 7 7 ;
        12 12 11 11 10 10 9 9 8 8 7 7 ;
        12 12 11 11 10 10 9 9 8 8 7 7 ];
   
pin=[   1  5  1  5  1  5  1  5  1  5  1  5 ;
        2  6  2  6  2  6  2  6  2  6  2  6 ;
        3  7  3  7  3  7  3  7  3  7  3  7 ;
        4  8  4  8  4  8  4  8  4  8  4  8 ;
        5  1  5  1  5  1  5  1  5  1  5  1 ;
        6  2  6  2  6  2  6  2  6  2  6  2 ;
        7  3  7  3  7  3  7  3  7  3  7  3 ;
        8  4  8  4  8  4  8  4  8  4  8  4 ];
    
for ii=1:8
    ts_temp=zeros(1,12);
    ind_mat=(pin==ii);
    ts_temp(dac(ind_mat))=tuning_state(ind_mat);
    ts_temp=fliplr(ts_temp);
    msg='15';
    for jj=1:12
        msg=[msg ' ' num2str(4096*ii+16*ts_temp(jj))];
    end
    msg=[msg ' '];
    byt = a.BytesAvailable;
    if (byt > 0)
        fread(a,byt);
    end
    fprintf(a,msg);
    while (a.BytesAvailable < 3)
    end 
    fread(a,3);
end

