---
title: "[最大流, Edmonds–Karp算法] shuttle 太空飞行计划"
date: 2011-03-05
category: Programming
tags: 算法 网络流 C/C++ STL
layout: post
---

**问题描述**

W 教授正在为国家航天中心计划一系列的太空飞行。每次太空飞行可进行一系列商业性实验而获取利润。现已确定了一个可供选择的实验集合 E={E1，E2，…，Em}，和进行这些实验需要使用的全部仪器的集合I={I1， I2，…In}。 实验 Ej需要用到的仪器是 I的子集。配置仪器Ik的费用为ck美元。实验Ej的赞助商已同意为该实验结果支付pj美元。W教授的任务是找出一个有效算法， 确定在一次太空飞行中要进行哪些实验并因此而配置哪些仪器才能使太空飞行的净收益最大。这里净收益是指进行实验所获得的全部收入与配置仪器的全部费用的差额。

**数据输入**

由文件input.txt提供输入数据。文件第 1行有 2 个正整数 m和 n。m是实验数，n是仪器数。接下来的 m 行，每行是一个实验的有关数据。第一个数赞助商同意支付该实验的费
 用；接着是该实验需要用到的若干仪器的编号。最后一行的 n个数是配置每个仪器的费用。

**结果输出**

程序运行结束时，将最佳实验方案输出到文件 output.txt 中。第 1 行是实验编号；第 2行是仪器编号；最后一行是净收益。

**样例**

shuttle.in

```plain
2 3
10 1 2
25 2 3
5 6 7
```
shuttle.out

```bash
1 2
1 2 3
17
```


《算法导论》上思考题有这个，这类问题的专业说法是“最大权闭合图”，用网络流解决。

关键在于如何建立网络流模型，网上有很好的讲解： [http://blog.imzzl.com/2010/01/113.html](http://blog.imzzl.com/2010/01/113.html)

至于如何求收益最大时进行的实验和需要的器材，搜索残余网络得到最小割，输出源点所在部分的结点就行了。

我用的Edmonds–Karp算法（即BFS版本的Ford–Fulkerson）求最大流，以下是C++代码，练习了STL：



```cpp
#include <iostream>
#include <fstream>
#include <cstring>
#include <vector>
#include <queue>

using namespace std;

const int INFFLOW = 0x7FFFFFFF;

struct ST_PATH {
	int c, end;
};

vector<ST_PATH> *map;

void addpath (const int u, const int v, const int c)
{	//向邻接表添加容量为c的边(u,v), 以及退流用的反向边(v,u)
	ST_PATH newp;

	newp.end = v;
	newp.c = c;
	map[u].push_back(newp);

	newp.end = u;
	newp.c = 0;
	map[v].push_back(newp);
}

int main (void)
{
	ifstream fin("shuttle.in");
	ofstream fout("shuttle.out");

	//读取数据及初始化
	int M, N, total=0;
	fin >> M >> N;
	map = new vector<ST_PATH> [M+N+2];
	for (int i=1; i<=M; i++)
	{
		int tmp;
		fin >> tmp;
		total += tmp;
		addpath(0, i, tmp);

		while (fin.get() != '\n')
		{ //Windows会读出错, 可以改成'\t'或者用stringstream什么的
			fin >> tmp;
			addpath(i, M+tmp, INFFLOW);
		}
	}

#define T (M+N+1)
	for (int i=M+1; i<=M+N; i++)
	{
		int c;
		fin >> c;
		addpath(i, T, c);
	}

	//Edmonds–Karp算法部分
	queue<int> q;
	int pflow[T+1], father[T+1], flow[T+1][T+1], maxflow = 0;
	memset(flow, 0, sizeof(flow));
	while (1)
	{
		memset(pflow, 0, sizeof(pflow));
		pflow[0] = INFFLOW;
		q.push(0);

		while (!q.empty())
		{
			int curr = q.front();
			q.pop();
			for (vector<ST_PATH>::iterator pi = map[curr].begin();
					pi < map[curr].end();  pi++)
			{
				int fl;
				if (!pflow[pi->end]  &&
						(fl = pi->c - flow[curr][pi->end]) > 0)
				{
					pflow[pi->end] = pflow[curr] > fl  ?  fl : pflow[curr];
					father[pi->end] = curr;
					q.push(pi->end);
				}
			}
		}

		if (!pflow[T])
			break;

		maxflow += pflow[T];
		for (int i=T; i; i=father[i])
			flow[father[i]][i] += pflow[T],
			flow[i][father[i]] -= pflow[T];
	}
	
	//从残留网络获取最小割包含原点的部分
	bool boo[M+N+1];
	memset(boo, 0, sizeof(boo));
	q.push(0);
	while (!q.empty())
	{
		int curr = q.front();
		q.pop();
		for (vector<ST_PATH>::iterator pi = map[curr].begin();
				pi < map[curr].end();  pi++)
			if (!boo[pi->end]  &&  pi->c - flow[curr][pi->end] > 0)
			{
				boo[pi->end] = true;
				q.push(pi->end);
			}
	}
	
	//输出部分
	for (int i=1; i<=M; i++)
		if (boo[i])
			fout << i << ' ';
	fout << endl;

	for (int i=M+1; i<=M+N; i++)
		if (boo[i])
			fout << i-M << ' ';
	fout << endl;

	fout << total - maxflow << endl;

	fin.close();
	fout.close();

	return 0;
}
```
