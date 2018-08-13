1. by{length|5|number~end}{type=0x0A}{number|1byte}{x|2byte}{y|2byte}\r\n
1. `length`以字节为单位，为`5`
1. `number`缺省值待确认（为`0`）
1. `x`, `y`均带符号
1. 小端
1. 符号位以`struct.pack`为准
1. 波特率: 115200
