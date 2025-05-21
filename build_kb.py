import pathlib, glob, pickle, os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

SRC_DIR   = pathlib.Path("knowledge")
INDEX_DIR = pathlib.Path("indices/ospf_faiss")

def load_docs() -> list[Document]:
    docs = []
    for path in SRC_DIR.glob("**/*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append(Document(page_content=text, metadata={"source": str(path)}))
    return docs

def main():
    docs = load_docs()
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    chunks = splitter.split_documents(docs)
    print(f"Loaded {len(docs)} docs → {len(chunks)} chunks")

    embeddings = OpenAIEmbeddings()
    vector_db  = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vector_db.save_local(INDEX_DIR.as_posix())
    print(f"Index saved to {INDEX_DIR}")

if __name__ == "__main__":
    main()
