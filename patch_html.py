with open('template.html', 'r') as f:
    code = f.read()

# 1. Add Market badge to Active Positions cards
code = code.replace(
'''<h3 class="text-xl font-bold text-white mb-2">{{ pos.symbol }}</h3>''',
'''<h3 class="text-xl font-bold text-white mb-2">{{ pos.symbol }} <span class="text-xs font-normal ml-2 px-2 py-1 bg-slate-700 text-slate-300 rounded">{{ pos.currency }}</span></h3>'''
)

# 2. Add Market column header to Trade History table
code = code.replace(
'''<th class="px-6 py-4 text-left font-semibold">Symbol</th>
                                <th class="px-6 py-4 text-left font-semibold">Action</th>''',
'''<th class="px-6 py-4 text-left font-semibold">Symbol</th>
                                <th class="px-6 py-4 text-left font-semibold">Market</th>
                                <th class="px-6 py-4 text-left font-semibold">Action</th>'''
)

# 3. Add Market column value to Trade History rows
code = code.replace(
'''<td class="px-6 py-4 font-bold text-white">{{ trade.symbol }}</td>
                                <td class="px-6 py-4"><span class="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-semibold">{{ trade.action }}</span></td>''',
'''<td class="px-6 py-4 font-bold text-white">{{ trade.symbol }}</td>
                                <td class="px-6 py-4 text-slate-400 text-sm">{{ trade.currency }}</td>
                                <td class="px-6 py-4"><span class="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-semibold">{{ trade.action }}</span></td>'''
)

with open('template.html', 'w') as f:
    f.write(code)
