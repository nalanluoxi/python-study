from langchain_community.embeddings import ZhipuAIEmbeddings

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader

import re
from langchain_text_splitters import RecursiveCharacterTextSplitter



# 创建一个 PyMuPDFLoader Class 实例，输入为待加载的 pdf 文档路径
loader = PyMuPDFLoader("/Users/nalan/IdeaProjects/python-test/py/ReadParquetData/aiTest/data/pumpkin_book.pdf")

# 调用 PyMuPDFLoader Class 的函数 load 对 pdf 文件进行加载
pdf_pages = loader.load()
#print(f"载入后的变量类型为：{type(pdf_pages)}，",  f"该 PDF 一共包含 {len(pdf_pages)} 页")

pdf_page = pdf_pages[34]
#print(f"每一个元素的类型：{type(pdf_page)}.",
#      f"该文档的描述性数据：{pdf_page.metadata}",
#      f"查看该文档的内容:\n{pdf_page.page_content}",
#      sep="\n------\n")
#print("修改后的\n")
pattern = re.compile(r'[^\u4e00-\u9fff](\n)[^\u4e00-\u9fff]', re.DOTALL)
pdf_page.page_content = re.sub(pattern, lambda match: match.group(0).replace('\n', ''), pdf_page.page_content)
#print(pdf_page.page_content)
#print("修改第二次后的\n")
pdf_page.page_content = pdf_page.page_content.replace('•', '')
pdf_page.page_content = pdf_page.page_content.replace(' ', '')
#print(pdf_page.page_content)


# 知识库中单段文本长度
CHUNK_SIZE = 500

# 知识库中相邻文本重合长度
OVERLAP_SIZE = 50

# 使用递归字符文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP_SIZE
)
temp = text_splitter.split_text(pdf_page.page_content[0:1000])
#print(temp)
split_docs = text_splitter.split_documents(pdf_pages)
# 定义 Embeddings
# embedding = OpenAIEmbeddings()
embedding = ZhipuAIEmbeddings()
# embedding = QianfanEmbeddingsEndpoint()

# 定义持久化路径
persist_directory = '/Users/nalan/IdeaProjects/python-test/py/ReadParquetData/aiTest/data'


vectordb = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding,
    persist_directory=persist_directory  # 允许我们将persist_directory目录保存到磁盘上
)

print(f"向量库中存储的数量：{vectordb._collection.count()}")


