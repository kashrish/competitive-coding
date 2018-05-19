#include <bits/stdc++.h>
#define mp make_pair
#define pb push_back
#define MOD 1000000007
#define PI 3.14159265359
#define ff first
#define ss second
#define MAX(X,Y)  (X>Y ? X:Y)
#define MIN(X,Y)  (X<Y ? X:Y)
using namespace std;

typedef long long ll;
typedef vector<int> vi;
typedef pair<int,int> pi;
typedef vector<pi > vpi;

#define MAXN  100002
vi g[MAXN];
int L[MAXN],p[MAXN];
int P[MAXN][19];
void preProLCA(int n){
    int i,j;
    
    for(i=1;i<=n;i++){
        for(j=0;1<<j <= n ;j++){
            P[i][j]=-1;
        }
    }
    
    for(i=1;i<=n;i++) P[i][0]=p[i];
    
    for (j = 1; 1 << j <= n; j++){
        for (i = 1; i <= n; i++){
             if (P[i][j - 1] != -1)
                 P[i][j] = P[P[i][j - 1]][j - 1];
        }
    }
}

int LCA(int u,int v){
    if(L[u]<L[v]) swap(u,v);
    int lg,i;
    for (lg = 1; 1 << lg <= L[u]; lg++);
      lg--;
    for(i=lg;i>=0;i--){
        if(L[u]- (1<<i) >= L[v]) u=P[u][i];
    }
    if(u==v) return u;
    for(i=lg;i>=0;i--){
        if(P[u][i]!=-1 and P[u][i]!=P[v][i])
            u=P[u][i],v=P[v][i];
    }
    return p[u];
}
void dfs(int s){
    
    if(s==1) {L[s]=0;p[s]=0;}
    
    for(int i=0;i<g[s].size();i++){
        int v=g[s][i];
        if(L[v]==-1){
            L[v]=L[s]+1;
            p[v]=s;
            dfs(v);
        }
    }
}
int findAns(int s,int f,int t){
    int lsf,lst,lft,ans;
    lsf=LCA(s,f);  lst=LCA(s,t);  lft=LCA(f,t);
    if(L[lft] < L[lsf]){
        ans=L[f]-L[lsf]+1;
    }
    else if(lft==lsf){
    
        if(lst == s){
            ans=L[f]-L[lsf]+1 + L[s]-L[lsf];
        }
        else{
            ans=L[f]-L[lsf]+1 + L[lst]-L[lsf];
        }
    }
    else if(L[lsf]<L[lft]){
        
        if(L[lft] < L[f]) ans=L[f]-L[lft]+1 ;
        else ans=1;
    }
    return ans;
}
int main() {
    
    ios:: sync_with_stdio(0);
    cin.tie(NULL),cout.tie(NULL);
    int n,q,inp,i;
    cin>>n>>q;
    memset(L,-1,sizeof L);
    for(i=2;i<=n;i++){
        cin>>inp;
        g[inp].pb(i);
        g[i].pb(inp);
        
    }
    dfs(1);
    preProLCA(n);
    while(q--){
        int a,b,c,ans;
        cin>>a>>b>>c;
        ans=findAns(a,b,c);
        ans=max(ans,findAns(a,c,b));
        ans=max(ans,findAns(b,a,c));
        ans=max(ans,findAns(b,c,a));
        ans=max(ans,findAns(c,b,a));
        ans=max(ans,findAns(c,a,b));
        cout<<ans<<endl;
        
        
        
    }
	return 0;
}
