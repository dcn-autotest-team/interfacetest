DCN = """
██████╗  ██████╗███╗   ██╗
██╔══██╗██╔════╝████╗  ██║
██║  ██║██║     ██╔██╗ ██║
██║  ██║██║     ██║╚██╗██║
██████╔╝╚██████╗██║ ╚████║   
╚═════╝  ╚═════╝╚═╝  ╚═══╝ 
"""
dst = 'E:\\wirelessinterfacetest\\interfacetest\\testcase'  # 设置成你实际testcase目录

def change(matched):
    """
    >>> '11'.zfill(3)
    '011'
    >>> '11'.zfill(5)
    '00011'
    >>> '1'.zfill(5)
    '00001'
    """
    # 注意group("num")中num要有“”包裹起来
    num = matched.group("num")  # 通过小名num取到具体的值，其实也可以用默认的int类型的1取到值(但是不pythonic)
    return '_'+str(num).zfill(3)+'_'  # zfill用法见上，刚好此处只需加0所以用zfill，如果复杂例如填充其他字符！@#￥等就要
    #用到format或者%或者（f‘{}’ python3.5还是3.6之后新语法忘记了）进行格式化输出，如果更复杂那就要设计类重写__format__方法

os.chdir(dst) # 进入到dst方便后面os.rename的时候不用管路径前缀，只关心具体的文件名称    
for i in os.scandir(dst):
    #正则表达式?P<num>相当于给匹配到的内容\d+取了个小名叫num
    # re.sub可以接受函数作为第二个参数，严谨的说是callable对象作为第二个参数，
    # 会将匹配到的match object传递给次例中的change作为参数
    # os.scandir返回一个生成器，值的内容为DirEntry，具有2个默认属性一个path 一个name我们用到了name
    # 不用os.listdir的原因第一占用内存返回值为list对象，第二list取值通过index取值，这种取法不是很pythonic
    # 代码不易阅读，同时如果要处理全路径的时候还要进行os.join(dst,value)，重复不讨好，os.scandir直接.path即可
    # os.walk其实性能更高功能更全，用于处理比较复杂的全盘文件扫描，但是此处用不合适也没必要
    """
    def sub(pattern, repl, string, count=0, flags=0):
    Return the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern in string by the
    replacement repl.  repl can be either a string or a callable;
    if a string, backslash escapes in it are processed.  If it is
    a callable, it's passed the match object and must return
    a replacement string to be used.
    """
    # os.rename还有个兄弟叫做os.renames有兴趣可以参考pycharm进去看看
    os.rename(i.name, re.sub(r'(?P<num>\d+)', change, i.name))

