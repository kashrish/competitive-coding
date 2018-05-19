#include <bits/stdc++.h>
#define mp make_pair
#define pb push_back
#define MOD 1000000007
#define PI 3.14159265359
#define ff first
#define ss second
#define MIN(x,y)   ((x<y)? x:y)
using namespace std;

typedef long long ll;
typedef vector<int> vi;
typedef pair<int,int> pi;
typedef vector<pi > vpi;


const int MAXN =5002; 
const ll INF = 1e18; 
 
struct edge {
	int a, b;
	ll cap, flow;
};
 
int n, s, t, d[MAXN], ptr[MAXN], q[MAXN];
vector<edge> e;
vector<int> g[MAXN];
 
void add_edge (int a, int b, ll cap) {
	edge e1 = { a, b, cap, 0LL };
	edge e2 = { b, a, cap, 0LL };
	g[a].push_back ((int) e.size());
	e.push_back (e1);
	g[b].push_back ((int) e.size());
	e.push_back (e2);
}
 
bool bfs() {
	int qh=0, qt=0;
	q[qt++] = s;
	for(int i=1;i<=n;i++){
	    d[i]=-1;
	}
	
	d[s] = 0;
	while(qh < qt && d[t] == -1) {  
		int v = q[qh++];
		for (int i=0; i<g[v].size(); ++i) {
			int id = g[v][i]  ,  to = e[id].b;
				
			if (d[to] == -1 && e[id].flow < e[id].cap) {
				q[qt++] = to;
				d[to] = d[v] + 1;
			}
		}
	}
	return d[t] != -1;
}
 
ll dfs (int v, ll flow) {
	if (flow==0LL)  return 0;
	if (v == t)  return flow;
	for (; ptr[v]< g[v].size(); ++ptr[v]) {
		int id = g[v][ptr[v]],
			to = e[id].b;
		if (d[to] != d[v] + 1)  continue;
		ll pushed = dfs (to, MIN(flow, e[id].cap - e[id].flow));
		if (pushed) {
			e[id].flow += pushed;
			e[id^1].flow -= pushed;
			return pushed;
		}
	}
	return 0;
}
 
ll dinic() {
	ll flow = 0,pushed;
	for (;;) {
		if (bfs()==false)  break;
		
		for(int i=1;i<=n;i++)
		    ptr[i]=0;
		while (pushed = dfs (s, INF)){
			flow += pushed;
		}
	}
	return flow;
}



int main() {
    
    ios:: sync_with_stdio(0);
    cin.tie(NULL),cout.tie(NULL);
    int m,i,a,b;
    ll c;
    cin>>n>>m;
    map< pi ,ll > eg;
    for(i=1;i<=m;i++){
        cin>>a>>b>>c;
        if(eg.find(mp(a,b))!=eg.end()){
            eg[mp(a,b)]+=c;
                
        }
        else if(eg.find(mp(b,a))!=eg.end()){
            eg[mp(b,a)]+=c;
                
        }
        else if(a!=b){
            eg[mp(a,b)]=c;
        }
    }
    map<pi ,ll> ::iterator it;
    
    for(it=eg.begin();it!=eg.end();++it){
        a=(*it).ff.ff;
        b=(*it).ff.ss;
        c=(*it).ss;
        add_edge(a,b,c);
    }
    s=1;  t=n;
    cout<<dinic();
    
	return 0;
}
