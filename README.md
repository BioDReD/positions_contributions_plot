# Positions Contributions Plot

Produce a plot of the contribution of the positions of a sequence. 
From a CSV file (semi colon separated) of the positions and the contributions percentage, a plot is created for the positions above a threshold.

Input CSV file example:

```
position;total;January 10th – January 30th;January 31st - February 20th;February 21st - May 10th
19;15,7449001427113;21,3443312654418;64,0545769483286;45,8731782495816
24;18,8579553625244;21,6835246318005;46,8953860337771;39,1922162237629
25;15,2060470301015;14,2810899310818;67,5092893961194;45,5677864765383
26;20,4549649017069;19,7230746054005;57,7648525570285;41,9583431750929
...
743;0,102399385525515;0;0,0139255446771758;0,985742136859037
744;0,106612460118228;0;0;1,7362689175026
745;0,0328520516517756;0;0;0
746;0,0419439085163738;0;0;0
747;0,0470362475361669;0;0;0
748;0,0586298295820305;0;0;0
```

The command to launch to create the plot for "January 10th – January 30th" period is:

```bash
./pcp.py --out results/period1.svg  --threshold 80 --position-col position --target-col "January 10th – January 30th" 
--log results/pcp_period1.log data/contributions.csv
```
