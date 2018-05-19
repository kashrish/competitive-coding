#include <bits/stdc++.h>
#define mp make_pair
#define pb push_back
#define MOD 1000000007
#define PI 3.14159265359
#define ff first
#define ss second

using namespace std;

typedef long long ll;
typedef vector<int> vi;
typedef pair<int,int> pi;
typedef vector<pi > vpi;

vi g[100005];
vi w[100005];
map<int,int> M;
map<int,int>::iterator it;
int Rhash[100005],SZ;

struct node{
    int data;
    node *left,*right;
    node(int data,node* L,node* R) : 
        data(data),left(L),right(R) {}
};
node *segT[100005];
void makeTree(node* root,int l,int r){
    if(l==r){
        root->data=0;
    }
    else{
        int m=(l+r)>>1;
        root->left=new node(0,NULL,NULL);
        root->right=new node(0,NULL,NULL);
        makeTree(root->left,l,m);
        makeTree(root->right,m+1,r);
    }
}
void insertNode(node *root,int l,int r,int x,node *par){
    
    if(l==r){
        root->data =(par->data) ^ Rhash[x];
        return ;
    }
    int m=(l+r)>>1;
    if(x<=m){
        root->right = par->right;
        root->left= new node(0,NULL,NULL);
        insertNode(root->left,l,m,x,par->left);
    }
    else{
        root->left = par->left;
        root->right = new node(0,NULL,NULL);
        insertNode(root->right,m+1,r,x,par->right);
    }
    root->data = (root->left->data)^(root->right->data);
}
int solve(node *root,int l,int r,int ql,int qr){
    if(ql>qr)  return 0;
    if(ql==l and qr==r){
        return root->data;
    }
    int m=(l+r)>>1;
    return solve(root->left,l,m,ql,min(qr,m) ) ^ solve(root->right,m+1,r,max(ql,m+1),qr);
}
void dfs(int v,int par,int C){
    
    if(v!=1) { 
        segT[v]=new node(0,NULL,NULL);
        insertNode(segT[v],1,SZ,C,segT[par]);
    }
    for(int i=0;i<g[v].size();i++){
        int adj=g[v][i];
        if(adj!=par){
            dfs(adj,v,M[ w[v][i] ] );
        }
    }
}

#define gc getchar_unlocked

inline void scanint(int &x)
{
    register int c = gc();
    x = 0;
    for(;(c<48 || c>57);c = gc());
    for(;c>47 && c<58;c = gc()) {x = (x<<1) + (x<<3) + c - 48;}
}

int BS(int x){
    int l,m,r;
    l=1; r=SZ;
    if(x<Rhash[l])  return -1;
    if(x>Rhash[r])  return SZ;
    while(l<=r){
        m=(l+r)>>1;
        if(x>=Rhash[m])
            l=m+1;
        else r=m-1;   
    }
    return r;
}

int main() {
    int T,n,i,u,v,C,m,k,res;
    scanint(T);
    while(T--){
        scanint(n);
        for(i=1;i<=n;i++) {
            g[i].clear(); w[i].clear();
        }
        M.clear();
        for(i=1;i<n;i++){
            scanint(u); scanint(v); scanint(C);
            M[C];
            g[u].pb(v); w[u].pb(C);
            g[v].pb(u); w[v].pb(C);
        }
        i=1;
        for(it=M.begin();it!=M.end();++it){
            M[it->ff]=i;
            Rhash[i]=it->ff;
            i++;
        }
        SZ=i-1;
        segT[1]=new node(0,NULL,NULL);
        makeTree(segT[1],1,SZ);
        dfs(1,0,0);
        
        scanint(m);
        while(m--){
            scanint(u); scanint(v); scanint(k);
            k=BS(k);
            if(k==-1) res=0;
            else res=solve(segT[u],1,SZ,1,k) ^ solve(segT[v],1,SZ,1,k);
            printf("%d\n",res);
        }
    }
	return 0;
}
