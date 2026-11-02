#################### STATUS BAR (shared by .wps and .sbs) ####################
%Fl(2,15-Noir-Mono.fnt)
%xl(B,battery.bmp,0,0,22)
%xl(L,lock.bmp,0,0)

# black strip behind the whole status bar (the rest of the theme is #1E1C1A)
%V(0,0,320,24,-)
%Vb(000000)

# left: playlist position "4/100"
%V(8,4,96,16,2)
%Vb(000000)
%Vf(FFFFFF)
%al%?mp<|%pp/%pe|%pp/%pe|%pp/%pe|%pp/%pe||||>

# hold lock right after the counter (counter width depends on digit count).
# 1x1 host viewport: it gets cleared on redraw, so it must not cover the counter.
%V(319,0,1,1,-)
%Vb(000000)
%?mh<%?mp<%Vd(lock0)|%?if(%pe,<,10)<%Vd(lock2)|%?if(%pe,<,100)<%?if(%pp,<,10)<%Vd(lock3)|%Vd(lock4)>|%?if(%pe,<,1000)<%?if(%pp,<,10)<%Vd(lock4)|%?if(%pp,<,100)<%Vd(lock5)|%Vd(lock6)>>|%?if(%pp,<,10)<%Vd(lock5)|%?if(%pp,<,100)<%Vd(lock6)|%?if(%pp,<,1000)<%Vd(lock7)|%Vd(lock8)>>>>>>|%?if(%pe,<,10)<%Vd(lock2)|%?if(%pe,<,100)<%?if(%pp,<,10)<%Vd(lock3)|%Vd(lock4)>|%?if(%pe,<,1000)<%?if(%pp,<,10)<%Vd(lock4)|%?if(%pp,<,100)<%Vd(lock5)|%Vd(lock6)>>|%?if(%pp,<,10)<%Vd(lock5)|%?if(%pp,<,100)<%Vd(lock6)|%?if(%pp,<,1000)<%Vd(lock7)|%Vd(lock8)>>>>>>|%?if(%pe,<,10)<%Vd(lock2)|%?if(%pe,<,100)<%?if(%pp,<,10)<%Vd(lock3)|%Vd(lock4)>|%?if(%pe,<,1000)<%?if(%pp,<,10)<%Vd(lock4)|%?if(%pp,<,100)<%Vd(lock5)|%Vd(lock6)>>|%?if(%pp,<,10)<%Vd(lock5)|%?if(%pp,<,100)<%Vd(lock6)|%?if(%pp,<,1000)<%Vd(lock7)|%Vd(lock8)>>>>>>|%?if(%pe,<,10)<%Vd(lock2)|%?if(%pe,<,100)<%?if(%pp,<,10)<%Vd(lock3)|%Vd(lock4)>|%?if(%pe,<,1000)<%?if(%pp,<,10)<%Vd(lock4)|%?if(%pp,<,100)<%Vd(lock5)|%Vd(lock6)>>|%?if(%pp,<,10)<%Vd(lock5)|%?if(%pp,<,100)<%Vd(lock6)|%?if(%pp,<,1000)<%Vd(lock7)|%Vd(lock8)>>>>>>|%Vd(lock0)|%Vd(lock0)|%Vd(lock0)|%Vd(lock0)>|>

# centre: date and time DD.MM.YYYY H:mm
%V(96,4,128,16,2)
%Vb(000000)
%Vf(FFFFFF)
%ac%cd.%cm.%cY %cH:%cM

# right: battery percent + macOS-style battery
%V(224,4,56,16,2)
%Vb(000000)
%Vf(FFFFFF)
%ar%bl%%
%V(284,6,28,13,-)
%Vb(000000)
%?bp<%?bc<%?bl<%xd(Bl)|%xd(Bm)|%xd(Bn)|%xd(Bo)|%xd(Bp)|%xd(Bq)|%xd(Br)|%xd(Bs)|%xd(Bt)|%xd(Bu)|%xd(Bv)>|%xd(Bv)>|%?bl<%xd(Ba)|%xd(Bb)|%xd(Bc)|%xd(Bd)|%xd(Be)|%xd(Bf)|%xd(Bg)|%xd(Bh)|%xd(Bi)|%xd(Bj)|%xd(Bk)>>

#################### END STATUS BAR ####################
