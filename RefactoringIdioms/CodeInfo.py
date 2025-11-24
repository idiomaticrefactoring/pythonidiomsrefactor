class CodeInfo():
    def __init__(self, file_path="" ,idiom="",cl="",me="",
                 compli_code="", simple_cod="",lineno=[]):
        self.file_path = file_path
        self.cl = cl
        self.me = me
        self.idiom = idiom
        self.compli_code = compli_code
        self.simple_code = simple_cod
        self.lineno=lineno
    def lineno_str(self):
        linestr=""
        line_list=[]
        for e_lineno_start,e_lineno_end in self.lineno:
            if not line_list:
                line_list.append([e_lineno_start,e_lineno_end])
            else:
                if e_lineno_start-line_list[-1][-1]<=1:
                    line_list[-1][-1]=e_lineno_end
                else:
                    line_list.append([e_lineno_start, e_lineno_end])
        linestr=[]
        for start,end in line_list:
            linestr.append(f"lines {start} to {end}")
        return ", ".join(linestr)

    def full_info(self):
        return "***".join(["Filepath: "+self.file_path, "Class: "+self.cl if self.cl else '', "Method: "+self.me if self.me else '',"Idiom: "+self.idiom,self.code_str()])

    def code_str(self):
        lineno_str=self.lineno_str()
        codestr=f"***{lineno_str}\n"
        return "".join([codestr,self.compli_code,"\n-----is refactored into----->\n",self.simple_code])


