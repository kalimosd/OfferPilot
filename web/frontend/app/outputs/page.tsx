"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { getOutputs, getFileUrl, deleteFile } from "@/lib/api";
import ReactMarkdown from "react-markdown";

const TABS = [
  { value: "resumes", label: "Resumes" },
  { value: "research", label: "Research" },
  { value: "interview", label: "Interview" },
  { value: "pipeline", label: "Pipeline" },
  { value: "misc", label: "Misc" },
];

interface FileItem {
  name: string;
  type: string;
  size?: number;
  modified?: number;
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(ts: number) {
  return new Date(ts * 1000).toLocaleDateString("zh-CN");
}

export default function OutputsPage() {
  const [tab, setTab] = useState("resumes");
  const [files, setFiles] = useState<FileItem[]>([]);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    getOutputs(tab).then((res) => setFiles(res.files || []));
  }, [tab]);

  function handleTabChange(value: string) {
    setPreview(null);
    setTab(value);
  }

  async function handlePreview(name: string) {
    if (name.endsWith(".md")) {
      const url = getFileUrl(tab, name);
      const res = await fetch(url);
      const text = await res.text();
      setPreview(text);
    } else {
      window.open(getFileUrl(tab, name), "_blank");
    }
  }

  async function handleDelete(name: string) {
    if (!confirm(`删除 ${name}？`)) return;
    await deleteFile(tab, name);
    setFiles((prev) => prev.filter((f) => f.name !== name));
    if (preview) setPreview(null);
  }

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-zinc-200 px-6 py-3">
        <h1 className="text-sm font-semibold">Outputs</h1>
      </div>

      <Tabs value={tab} onValueChange={handleTabChange} className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="mx-6 mt-3 w-fit">
          {TABS.map((t) => (
            <TabsTrigger key={t.value} value={t.value} className="text-xs">{t.label}</TabsTrigger>
          ))}
        </TabsList>

        <div className="flex flex-1 overflow-hidden">
          <div className="w-1/2 border-r border-zinc-100 overflow-y-auto px-6 py-3">
            {files.length === 0 ? (
              <p className="text-zinc-400 text-sm mt-10 text-center">暂无文件</p>
            ) : (
              <div className="space-y-1">
                {files.filter((f) => f.type !== "dir").map((f) => (
                  <div key={f.name} className="flex items-center justify-between py-2 px-3 rounded hover:bg-zinc-50 group">
                    <button onClick={() => handlePreview(f.name)} className="text-left flex-1 min-w-0">
                      <p className="text-sm truncate">{f.name}</p>
                      <p className="text-xs text-zinc-400">
                        {f.size ? formatSize(f.size) : ""} {f.modified ? `· ${formatDate(f.modified)}` : ""}
                      </p>
                    </button>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {f.name.endsWith(".pdf") && (
                        <a href={getFileUrl(tab, f.name)} download><Button variant="ghost" size="sm" className="text-xs h-7">⬇</Button></a>
                      )}
                      <Button variant="ghost" size="sm" className="text-xs h-7 text-red-500" onClick={() => handleDelete(f.name)}>✕</Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="w-1/2 overflow-y-auto px-6 py-3">
            {preview ? (
              <div className="prose prose-sm prose-zinc max-w-none">
                <ReactMarkdown>{preview}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-zinc-400 text-sm mt-10 text-center">点击文件预览</p>
            )}
          </div>
        </div>
      </Tabs>
    </div>
  );
}
