#include <bits/stdc++.h>
#define mp make_pair
#define pb push_back
#define MOD 1000000007
#define PI 3.14159265359
#define ff first
#define ss second
#define gc getchar_unlocked
using namespace std;
 
typedef long long ll;
typedef vector<int> vi;
typedef pair<int,int> pi;
typedef vector<pi > vpi;
                                               //  spoj      problem          QTREE    solution
void scanint(int &x)
{
    register int c = gc();
    x = 0;
    for(;(c<48 || c>57);c = gc());
    for(;c>47 && c<58;c = gc()) {x = (x<<1) + (x<<3) + c - 48;}
}
#define N  10003
#define LN 14
vi g[N];
vi costs[N];
vi indexx[N];
int depth[N],pa[14][N],subsize[N],otherEnd[N];
int chainNo , chainInd[N] , chainHead[N] , posInBase[N];
int baseArray[N],ptr;
int st[N*6],qt[N*6];
 
void make_tree(int v,int tl,int tr){
    if(tl==tr){
        st[v]=baseArray[tl];
        return;
    }
    int tm=(tl+tr)>>1;
    make_tree(v*2,tl,tm);
    make_tree(v*2+1,tm+1,tr);
    st[v]= max(st[v*2],st[v*2+1]);
}
 
int query_tree(int v,int tl,int tr,int l,int r){
    if (l > r)
		return 0;
	if (l == tl && r == tr)
		return st[v];
	int tm = (tl + tr)>>1;
	return max(query_tree(v*2, tl, tm, l, min(r,tm)),
		        query_tree(v*2+1, tm+1, tr, max(l,tm+1), r) );
}
 
void update_tree(int v,int s,int e,int x,int val){
    if(s==e){
        st[v]=val;
    }
    else{
        int m=(s+e)>>1;
        if(x<=m){
            update_tree(v*2,s,m,x,val);
        }
        else{
            update_tree(v*2+1 ,m+1,e,x,val);
        }
        st[v]= max(st[v*2],st[v*2+1]);
    }
}
 
int query_up(int u,int v){
    if(u==v) return 0;
    int uchain,vchain=chainInd[v],ans=-1;
    //cout<<u<<v<<endl;
    while(1){
        uchain=chainInd[u];
        if(uchain==vchain){
            if(u==v)  break;
            
            ans=max(ans,query_tree(1, 0, ptr-1, posInBase[v]+1, posInBase[u]) );
            break;
        }
        
        ans=max(ans,query_tree(1,0,ptr-1,posInBase[chainHead[uchain]], posInBase[u]) );
        u=chainHead[uchain];
        u=pa[0][u];
    }
    return ans;
}
 
void HLD(int curr,int cost,int prev){
    if(chainHead[chainNo]==-1){
        chainHead[chainNo]=curr;
    }
    //cout<<curr<<endl;
    chainInd[curr]=chainNo;
    posInBase[curr]=ptr;
    baseArray[ptr++]=cost;
    
    int sc=-1,ncost;
    for(int i=0;i<g[curr].size();i++){
        int v=g[curr][i];
        if(v!=prev){
            if(sc==-1 || subsize[sc]<subsize[v]){
                sc=v;
                ncost=costs[curr][i];
            }
        }
    }
    if(sc!=-1){
        HLD(sc,ncost,curr);
    }
    for(int i=0;i<g[curr].size();i++){
        int v=g[curr][i];
        if(v!=prev && v!=sc){
            chainNo++;
            HLD(v,costs[curr][i],curr);
        }
    }
    
}
 
void dfs(int curr,int prev){
    depth[curr]=depth[prev]+1;
    subsize[curr]=1;
    pa[0][curr]=prev;
    for(int i=0;i<g[curr].size();i++){
        int v=g[curr][i];
        if(v!=prev){
            otherEnd[indexx[curr][i]]=v;
            dfs(v,curr);
            subsize[curr]+=subsize[v];
        }
    }
}
 
int LCA(int u, int v) {
	if(depth[u] < depth[v]) swap(u,v);
	int diff = depth[u] - depth[v];
	for(int i=0; i<LN; i++) if( (diff>>i)&1 ) u = pa[i][u];
	if(u == v) return u;
	for(int i=LN-1; i>=0; i--) if(pa[i][u] != pa[i][v]) {
		u = pa[i][u];
		v = pa[i][v];
	}
	return pa[0][u];
}
 
void query(int u, int v) {
	
	int lca = LCA(u, v);
	//cout<<lca<<endl;
	int ans = max( query_up(u, lca) , query_up(v, lca) ); 
	printf("%d\n", ans);
}
 
void change(int i,int val){
    int u=otherEnd[i];
    update_tree(1, 0, ptr-1, posInBase[u], val);
}
 
 
int main() {
    
    int T;
    scanint(T);
    while(T--){
        int i,n,u,v,c;
        scanint(n);
        for(i=0;i<=n;i++){
            g[i].clear(); indexx[i].clear(); costs[i].clear();
            for(int j=0; j<LN; j++) pa[j][i] = -1;
            chainHead[i]=-1;
        }
        for(i=1;i<=n-1;i++){
            scanint(u);  scanint(v);  scanint(c);
            g[u].pb(v);  costs[u].pb(c);  indexx[u].pb(i);
            g[v].pb(u);  costs[v].pb(c);  indexx[v].pb(i);
        }
        chainNo=0;
        ptr=0;
        depth[0]=0;
        dfs(1,0);
        HLD(1,0,0);
        make_tree(1,0,ptr-1);
        for(int i=1; i<LN; i++)
			for(int j=0; j<=n; j++)
				if(pa[i-1][j] != -1)
					pa[i][j] = pa[i-1][pa[i-1][j]];
		while(1) {
		    char s[10];
			scanf(" %s",s);
			if(s[0]=='D') {
				break;
			}
			int a, b;
			scanint(a); scanint(b);
			//cout<<"hello"<<endl;
			if(s[0]=='Q') {
				query(a, b);
			} else {
				change(a, b);
			}
		}
		
    }
    
	return 0;
}