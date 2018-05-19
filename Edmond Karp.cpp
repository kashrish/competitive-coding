#include <bits/stdc++.h>
#define mp make_pair
#define pb push_back
#define MOD 1000000007
#define PI 3.14159265359
#define ff first
#define ss second
 
//   ****************    MAX FLOW CODECHEF  RECEIPT RECOVERY EDMOND KARP ***********           
using namespace std;
 
typedef long long ll;
typedef vector<int> vi;
typedef pair<int,int> pi;
typedef vector<pi > vpi;
int flow[205][205];
int main() {
    
    ios:: sync_with_stdio(0);
    cin.tie(NULL),cout.tie(NULL);
    int T;
    cin>>T;
    while(T--){
        int n,m,i,j,N,a,b;
        cin>>n>>m;
        N=2*n+2;
        for(i=0;i<N;i++)
            for(j=0;j<N;j++)
                flow[i][j]=0;
        
        for(i=0;i<n;i++){
            flow[0][i+1]=flow[n+i+1][2*n+1]=1;
        }
        for(i=0;i<m;i++){
            cin>>a>>b;
            if(a!=b)
                flow[a][n+b]=1;
        }
        int f=0;
        int p[205];
        while(1){
            queue<int> q;
            memset(p,-1,sizeof p);
            q.push(0);
            p[0]=0;
            while(!q.empty()){
                int s=q.front();
                q.pop();
                for(i=0;i<N;i++){
                    if(flow[s][i]>0 && p[i]==-1){
                        p[i]=s;
                        q.push(i);
                    }
                }
            }
            if(p[N-1]==-1)
                break;
            f++;
            int tmp=N-1;
            while(tmp>0){
                flow[p[tmp]][tmp]--;
                flow[tmp][p[tmp]]++;
                tmp=p[tmp];
            }
        }
        cout<<n-f<<endl;
    }
    
	return 0;
}