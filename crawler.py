import requests
import json
import warnings
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib3.exceptions import InsecureRequestWarning
import os

# Fix UnicodeEncodeError on Windows GBK terminals
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

warnings.simplefilter('ignore', InsecureRequestWarning)

print("=== 爬虫升级版第二阶段：招聘数据分析 + 可视化 ===")

url = "https://jsonplaceholder.typicode.com/posts"

print("正在抓取基础数据...")
response = requests.get(url, verify=False)

if response.status_code == 200:
    posts = response.json()
    print(f"✅ 请求成功！获取 {len(posts)} 条基础数据")

    print("正在生成模拟招聘数据...")
    np.random.seed(42)

    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '南京', '武汉']
    companies = ['字节跳动', '腾讯', '阿里', '百度', '华为', '小米', '网易', '京东']

    data = []
    for post in posts:
        city = np.random.choice(cities)
        company = np.random.choice(companies)
        salary = np.random.randint(8000, 45000)
        is_python = np.random.rand() > 0.6
        title = post['title'][:30] + (" - Python工程师" if is_python else " - 后端开发")

        data.append({
            'id': post['id'],
            'title': title,
            'company': company,
            'city': city,
            'salary': salary,
            'body': post['body'][:150] + '...'
        })

    df = pd.DataFrame(data)
    print(f"✅ 生成 {len(df)} 条模拟招聘数据完成")

    df = df.drop_duplicates(subset=['id'])
    df['salary'] = df['salary'].fillna(df['salary'].mean())
    df['city'] = df['city'].fillna('未知')

    print("\n" + "="*60)
    print("📊 招聘数据统计分析结果")
    print("="*60)

    avg_salary_all = df['salary'].mean()
    python_jobs = df[df['title'].str.contains('Python', na=False)]
    avg_salary_python = python_jobs['salary'].mean() if not python_jobs.empty else 0

    print(f"整体平均薪资：{avg_salary_all:,.0f} 元")
    print(f"Python岗位平均薪资：{avg_salary_python:,.0f} 元（共 {len(python_jobs)} 个岗位）")
    print(f"最高薪资：{df['salary'].max():,} 元")
    print(f"最低薪资：{df['salary'].min():,} 元")

    print("\n🏙️  城市分布 Top 5：")
    city_top5 = df['city'].value_counts().head(5)
    for city, count in city_top5.items():
        print(f"   {city}: {count} 个岗位 ({count/len(df)*100:.1f}%)")

    print("\n🏢  公司岗位数量 Top 5：")
    company_top5 = df['company'].value_counts().head(5)
    for comp, count in company_top5.items():
        print(f"   {comp}: {count} 个岗位")

    if os.path.exists("analysis.csv"):
        try:
            os.remove("analysis.csv")
        except PermissionError:
            print("⚠️ 请先关闭 Excel 后再运行！")
            exit()

    df.to_csv("analysis.csv", index=False, encoding="utf-8-sig")
    df.to_excel("analysis.xlsx", index=False)   # 推荐用这个
    print("\n✅ 文件保存完成：analysis.csv + analysis.xlsx")

        # ==================== 可视化图表（修复版） ====================
    print("\n正在生成可视化图表...")

    # 创建一个大画布
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('招聘数据可视化分析', fontsize=16, fontweight='bold')

    # 图1：薪资分布直方图 + KDE
    sns.histplot(df['salary'], bins=20, kde=True, color='skyblue', ax=axes[0, 0])
    axes[0, 0].set_title('薪资分布直方图')
    axes[0, 0].set_xlabel('薪资 (元)')
    axes[0, 0].set_ylabel('岗位数量')

    # 图2：城市分布 Top 8 柱状图
    city_top = df['city'].value_counts().head(8)
    sns.barplot(x=city_top.values, y=city_top.index, hue=city_top.index, palette='viridis', legend=False, ax=axes[0, 1])
    axes[0, 1].set_title('城市岗位分布 Top 8')
    axes[0, 1].set_xlabel('岗位数量')

    # 图3：Python vs 其他岗位平均薪资对比
    avg_by_type = pd.DataFrame({
        '类型': ['Python岗位', '其他岗位'],
        '平均薪资': [avg_salary_python, df[~df['title'].str.contains('Python')]['salary'].mean()]
    })
    sns.barplot(x='类型', y='平均薪资', data=avg_by_type, hue='类型', palette='Set2', legend=False, ax=axes[1, 0])
    axes[1, 0].set_title('Python岗位 vs 其他岗位平均薪资对比')
    axes[1, 0].set_ylabel('平均薪资 (元)')

    # 图4：各城市薪资箱线图
    sns.boxplot(x='salary', y='city', data=df, hue='city', palette='Set3', legend=False, ax=axes[1, 1])
    axes[1, 1].set_title('各城市薪资分布箱线图')
    axes[1, 1].set_xlabel('薪资 (元)')

    plt.tight_layout(rect=[0, 0, 1, 0.95])   # 留出标题空间

    # 保存图片（强制保存）
    save_path = "recruitment_analysis.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ 图表已保存为 {save_path}（高清300dpi）")

    plt.close()

    print("\n🎉 第二阶段全部完成！")
    print("   • analysis.xlsx 可以直接用 Excel 打开查看数据")
    print("   • recruitment_analysis.png 是可视化分析报告")

else:
    print("请求失败")