create  new class(model)

##  class Docxfile 文件管理

        filename , 
        about text(文档简介)
        type(docx,ppt, pdf)
        transtask bool （是否需要翻译）
        graphtask bool (知识图谱)
        share bool (是否分享)
        userversion bool (启用版本控制）

##  class Docxpages  文件内容

docs( docxfile  ) 文档 选择一个
        about string 文档简介
        order int 排序(default 0)
        title string 标题
        subtitle string 副标题
        subweight int 标题级别(0-10,0为正文，1为一级标题，2为二级标题...)
        content string 内容
        contentedittime time.Time 内容编辑时间
        contentedituser user 内容编辑人
        transcontent string EN翻译内容
        transnote string 翻译备注
        transcheck1 bool 翻译校对1
        transcheck2 bool 翻译校对2
        translast bool 翻译最后确认
        transmanger user 翻译负责人
        docmanger user 文档负责人
        version  int 版本号

