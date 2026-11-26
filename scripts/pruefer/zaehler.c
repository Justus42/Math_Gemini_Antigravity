/* Eigener Zaehler (Claude, 26.11.2026): zaehlt fehlende t-Tupel eines Arrays.
   Aufruf: zaehler DATEI t v [N k]   Exit 0 = alles gedeckt, 1 = Luecken, 2 = Formatfehler. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
int main(int argc,char**argv){
  if(argc<4){fprintf(stderr,"usage\n");return 2;}
  int t=atoi(argv[2]),v=atoi(argv[3]);
  long wantN=argc>4?atol(argv[4]):-1; int wantK=argc>5?atoi(argv[5]):-1;
  FILE*f=fopen(argv[1],"rb"); if(!f){perror("open");return 2;}
  fseek(f,0,SEEK_END); long sz=ftell(f); fseek(f,0,SEEK_SET);
  char*buf=malloc(sz+1); if(fread(buf,1,sz,f)!=(size_t)sz)return 2; buf[sz]=0; fclose(f);
  if(sz==0||buf[sz-1]!='\n'){fprintf(stderr,"FORMAT: kein Zeilenende am Schluss\n");return 2;}
  long N=0; for(long i=0;i<sz;i++) if(buf[i]=='\n')N++;
  int k=0; {long i=0; int inn=0; while(buf[i]!='\n'){ if(isdigit((unsigned char)buf[i])){if(!inn){k++;inn=1;}} else inn=0; i++; }}
  unsigned char*A=malloc((size_t)N*k);
  long pos=0;
  for(long r=0;r<N;r++){
    for(int c=0;c<k;c++){
      if(!isdigit((unsigned char)buf[pos])){fprintf(stderr,"FORMAT Zeile %ld Spalte %d\n",r+1,c+1);return 2;}
      long x=0; int nd=0; while(isdigit((unsigned char)buf[pos])){x=x*10+(buf[pos]-'0');pos++;nd++; if(x>=v){fprintf(stderr,"FORMAT: Symbol >= v in Zeile %ld\n",r+1);return 2;}}
      if(nd>1&&buf[pos-nd]=='0'){fprintf(stderr,"FORMAT: fuehrende Null\n");return 2;}
      A[r*k+c]=(unsigned char)x;
      if(c<k-1){ if(buf[pos]!=' '){fprintf(stderr,"FORMAT Trenner Zeile %ld\n",r+1);return 2;} pos++; }
    }
    if(buf[pos]!='\n'){fprintf(stderr,"FORMAT Zeilenlaenge Zeile %ld\n",r+1);return 2;} pos++;
  }
  if((wantN>=0&&wantN!=N)||(wantK>=0&&wantK!=k)){fprintf(stderr,"FORMAT: N=%ld k=%d erwartet %ld %d\n",N,k,wantN,wantK);return 2;}
  if(t>k||t<1){fprintf(stderr,"t unzulaessig\n");return 2;}
  long vt=1; for(int i=0;i<t;i++)vt*=v;
  unsigned char*seen=malloc(vt);
  int idx[32]; for(int i=0;i<t;i++)idx[i]=i;
  unsigned long long missing=0, sets=0, badsets=0;
  for(;;){
    memset(seen,0,vt); long cnt=0;
    for(long r=0;r<N;r++){ const unsigned char*row=A+r*k; long h=0; for(int i=0;i<t;i++)h=h*v+row[idx[i]]; if(!seen[h]){seen[h]=1;cnt++;} }
    sets++; if(cnt!=vt){missing+=vt-cnt;badsets++;}
    int i=t-1; while(i>=0&&idx[i]==k-t+i)i--; if(i<0)break; idx[i]++; for(int j=i+1;j<t;j++)idx[j]=idx[j-1]+1;
  }
  printf("N=%ld k=%d t=%d v=%d Spaltenmengen=%llu davon_lueckenhaft=%llu fehlende_Tupel=%llu %s\n",N,k,t,v,sets,badsets,missing,missing?"FAIL":"PASS");
  return missing?1:0;
}
