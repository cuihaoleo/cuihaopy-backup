---
title: "[二项堆, 并查集] Monkey King 猴子选大王"
date: 2011-02-26
category: Programming
tags: 二项堆 算法 并查集 C/C++
layout: post
---

### **Monkey King 猴子选大王**
【问题描述】
 在一个森林里,住着N只好斗的猴子.开始,他们各自为政,互不相干.但是猴子们不能消除争吵,但这仅仅发生在两只互不认识的猴子之间.当争吵发生时,争吵的两只猴子都会求助他们各自最强壮的朋友,并且决斗.当然,决斗之后,两只猴子及他们所有的朋友都相互认识了,并且成为朋友,争吵将不会在他们之间发生.
 假定每一只猴子有一个强壮值,在每次决斗之后变为原来的一半(例如,10将为变为5,5将会变为2).
 假定每一只猴子认识他自己. 也就是当他发生争吵,并且自己是他的朋友中最强壮的,他将代表自己进行决斗.
  
 【输入格式】
 有几组测试数据,每组测试数据由两部分构成.
 第一部分:第一行有一个整数 N(N<=100,000),表示猴子的数量.下面有N行.每行有一个数,表示猴子的强壮值(<=32768).
 第二部分:第一行有一个整数M(M<=100,000),表示有M次争吵发生.下面有M行,每行有两个整数x和y,表示在第x只猴子和第y只猴子之间发生争吵.
  
 【输出格式】
 对于每一次争吵,如果两只猴子认识,输出-1,否则输出一个数,表示决斗后朋友中最强壮猴子的强壮值.

【输入输出样例】

monkeyk.in

```plain
5
20
16
10
10
4
5
2 3
3 4
3 5
4 5
1 5
```
monkeyk.out

```plain
8
5
5
-1
10
```


上个学期讲了二项堆，老师把这道题作为练习题。因为写起来比较复杂，一直没写。今天抽空搞定了。



因为要从猴子中不断选取最强壮的猴子，用堆记录体力值比较好。猴子认识后，还要进行堆合并操作，所以选择可合并堆数据结构——二项堆处理这道题比较合适。关于二项堆，参见[维基百科条目](http://zh.wikipedia.org/zh/%E4%BA%8C%E9%A1%B9%E5%A0%86)或者自己用各种搜索引擎查询，还可以参见《算法导论》相关章节，这部分能看懂的。



对于本题，显然应该用大头堆。减小节点key后的维护是向下移动的，比向上移动要麻烦且费时一些：每次移动从该节点子女中选出key最大的一个，与该节点key交换，一直下移key直到它小于所有子女。



另外，由于要判断每个猴子属于哪一个猴群，或者说所在的二项堆，我还用了并查集作为索引，并用了路径压缩优化。



下面是C语言代码。因为是第一次写二项堆，一些地方实现的不是太好，不过足够过这道题目了（代码太长，默认折叠了）。


```cpp
#include <stdio.h>
#include <stdlib.h>

/* 二项堆 */
struct ST_BH_HEAP;
struct ST_BH_NODE;

typedef struct ST_BH_NODE {
	int key, degree; //key:关键字  degree:下一层子女个数
	struct ST_BH_NODE *p, *son, *bro;
	//p:父节点  son:最左子节点  bro:右兄弟节点
} binheap_node; //二项堆节点(二项树)

typedef struct ST_BH_HEAP {
	struct ST_BH_NODE *head, *max, *tail;
	//head指向头节点, tail指向尾节点, max指向key最大的节点.
} binheap; //二项堆

/* 并查集 */
typedef struct ST_BCJ_NODE {
	struct ST_BH_HEAP *heap;
	struct ST_BCJ_NODE *p;
} bcj_node;

/* 全局变量 */
binheap_node *mk; //存储二项堆的节点, 不与猴子编号对应
bcj_node *idx; //并查集的节点, idx[n]是第(n+1)只猴子的并查集元素

/* 
 * < bh_node_init 二项树节点初始化 >
 * 初始化二项树node, 关键字设为key.
 * 返回值是为该节点分配的二项堆.
 */
binheap *bh_node_init (binheap_node *node, const int key)
{
	node->degree = 0;
	node->key = key;
	node->p = node->son = node->bro = NULL;
	binheap *belong = malloc(sizeof(binheap)); //开始时, 为每个二项树节点分配一个新堆
	belong->head = node;
	belong->max = node;
	belong->tail = node;

	return belong;
}

/* 
 * < bh_heap_resetmax 维护堆max指针 >
 * 减小节点关键字后可能破坏二项堆max指针, 通过该操作重新设置max指针.
 */
void bh_heap_resetmax (binheap *heap)
{
	binheap_node *pi, *pmax = heap->head;
	
	for (pi=pmax->bro; pi; pi=pi->bro)
		if (pi->key > pmax->key)
			pmax = pi;

	heap->max = pmax;
}

/* 
 * < bh_node_dec 减小一个节点的关键字 >
 * 减小node的关键字到nkey.
 */
void bh_node_dec (binheap_node *node, const int nkey)
{
	node->key = nkey;
	while (node->son)
	{
		binheap_node *pi, *pmax;

		pmax = node->son;
		for (pi=node->son->bro; pi; pi=pi->bro)
			if (pi->key > pmax->key)
				pmax = pi;

		if (node->key < pmax->key)
		{
			int tmp = node->key;
			node->key = pmax->key;
			pmax->key = tmp;
			node = pmax;
		}
		else
			break;
	}
}

/* 
 * < bh_heap_linknode 链接二项树与二项堆 >
 * 把以node为根的二项树链接在binheap的末尾.
 */
void bh_heap_linknode (binheap *h, binheap_node *node)
{
	if (h->tail)
	{
		h->tail->bro = node;
		node->bro = NULL;
		h->tail = node;
		if (node->key > h->max->key)
			h->max = node;
	}
	else
	{
		h->head = h->tail = h->max = node;
		node->bro = NULL;
	}
}

/* 
 * < bh_node_union 合并二项树 >
 * 合并二项树na和nb, 返回合并后的新二项树。
 */
binheap_node *bh_node_union (binheap_node *na, binheap_node *nb)
{
	if (na->key < nb->key)
	{
		binheap_node *tmp = na;
		na = nb;
		nb = tmp;
	}

	nb->bro = na->son;
	nb->p = na;
	na->son = nb;
	na->bro = NULL;
	na->degree++;

	return na;
}

/* 
 * < bh_heap_deltail 删除二项堆末端的二项树 >
 * 从二项堆h中删除h->tail指向的二项树, 并完成指针链接的维护.
 * 后面合并堆操作用到的, 不是标准的二项堆操作.
 */
void bh_heap_deltail (binheap *h)
{
	if (h->tail == h->head)
		h->head = h->tail = h->max = NULL;
	else
	{
		binheap_node *pi = h->head, *pmax = h->head;

		while (pi->bro != h->tail)
		{
			pi = pi->bro;
			if (pi->key > pmax->key)
				pmax = pi;
		}

		pi->bro = NULL;
		h->tail = pi;
		h->max = pmax;
	}
}

/* 
 * < bh_heap_union 合并二项堆 >
 * 合并二项堆ha和hb, 并返回合并后的堆.
 * 自己想的方法, 和一般的实现不太一样, 不如一般的实现好.
 */
binheap *bh_heap_union (binheap *ha, binheap *hb)
{
	binheap *h = malloc(sizeof(binheap));
	h->head = h->tail = h->max = NULL;

	binheap_node *pa = ha->head,
				 *pb = hb->head;

	while (pa || pb)
	{
		binheap_node *add;

		if (pa && (!pb || pa->degree < pb->degree))
		{
			add = pa;
			pa = pa->bro;
		}
		else if (!pa || pa->degree > pb->degree)
		{
			add = pb;
			pb = pb->bro;
		}
		else
		{
			binheap_node *nexta = pa->bro, *nextb = pb->bro;
			add = bh_node_union(pa, pb);
			pa = nexta;
			pb = nextb;
		}

		if (!h->tail  ||  add->degree != h->tail->degree)
			bh_heap_linknode(h, add);
		else
		{
			add = bh_node_union(add, h->tail);
			bh_heap_deltail(h);
			bh_heap_linknode(h, add);
		}
	}

	free(ha);
	free(hb);

	return h;
}

/* 
 * < bcj_node_init 并查集元素初始化 >
 * 初始化元素node, 单独成一个集合, 指向的二项堆设为heap.
 */
void bcj_node_init (bcj_node *node, binheap *heap)
{
	node->p = NULL;
	node->heap = heap;
}

/* 
 * < bcj_getpa 查找元素最远祖先 >
 * 递归查找a的最远祖先, 并进行并查集的路径压缩优化.
 */
bcj_node *bcj_getpa (bcj_node *a)
{
	if (!a->p)
		return a;
	else
		return (a->p = bcj_getpa(a->p));
}

/* 
 * < bcj_union 集合合并 >
 * 合并元素a和b所在的并查集集合.
 */
void bcj_union (bcj_node *a, bcj_node *b)
{
	bcj_node *fa = bcj_getpa(a),
			 *fb = bcj_getpa(b);
	fb->p = fa;
}

/* 
 * < mk_fight 猴子对战 >
 * 模拟猴子(a+1)和猴子(b+1)的对战, 进行二项堆操作.
 * 返回题目要求输出的强壮值或者-1.
 */
int mk_fight (const int a, const int b)
{
	bcj_node *fa = bcj_getpa(idx+a),
			 *fb = bcj_getpa(idx+b);

	if (fa->heap == fb->heap)
		return -1;
	else
	{
		binheap *ha = fa->heap,
		        *hb = fb->heap;

		bh_node_dec(ha->max, (ha->max->key)>>1);
		bh_heap_resetmax(ha);
		bh_node_dec(hb->max, (hb->max->key)>>1);
		bh_heap_resetmax(hb);

		binheap *newheap = bh_heap_union(ha, hb);

		bcj_union(fa, fb);
		fa->heap = newheap;

		return newheap->max->key;
	}
}

/* 主程序 */
int main (void)
{
	FILE *fin = fopen("monkeyk.in", "r"),
	     *fout = fopen("monkeyk.out", "w");
	int n, m, i;

	fscanf(fin, "%d", &n);
	mk = malloc(n*sizeof(binheap_node));
	idx = malloc(n*sizeof(bcj_node));
	for (i=0; i<n; i++)
	{
		int str;
		fscanf(fin, "%d", &str);
		bcj_node_init(idx+i, bh_node_init(mk+i, str));
	}

	fscanf(fin, "%d", &m);
	for (i=0; i<m; i++)
	{
		int a, b;
		fscanf(fin, "%d %d", &a, &b);
		fprintf(fout, "%d\n", mk_fight(a-1, b-1));
	}

	fclose(fin);
	fclose(fout);

	return 0;
}
```
