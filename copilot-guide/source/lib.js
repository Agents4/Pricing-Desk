const d = require('docx');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, LevelFormat, Footer, PageNumber, AlignmentType,
} = d;

const W = 9360; // content width, US Letter with 1 inch margins

function runs(text, base = {}) {
  const parts = text.split('**');
  return parts.map((t, i) => new TextRun({ text: t, bold: i % 2 === 1 || base.bold, font: base.font, size: base.size, italics: base.italics, color: base.color }));
}

const border = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' };
const borders = { top: border, bottom: border, left: border, right: border };

function table(headers, rows, widths) {
  const sum = widths.reduce((a, b) => a + b, 0);
  if (sum !== W) throw new Error('widths must sum to ' + W + ' got ' + sum);
  const mk = (txt, w, head) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: head ? { fill: 'E8EEF5', type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: String(txt).split('\n').map((line) => new Paragraph({ children: runs(line, { bold: head, size: 20 }) })),
  });
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => mk(c, widths[i], false)) })),
    ],
  });
}

function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function inl(t){return esc(t).split('**').map((x,i)=>i%2?'<b>'+x+'</b>':x).join('');}
function html(blocks){
  const o=['<html><body>'];
  for(const b of blocks){
    if(b.title)o.push('<h1>'+esc(b.title)+'</h1>');
    else if(b.sub)o.push('<p><i>'+inl(b.sub)+'</i></p>');
    else if(b.h1)o.push('<h2>'+esc(b.h1)+'</h2>');
    else if(b.h2)o.push('<h3>'+esc(b.h2)+'</h3>');
    else if(b.p)o.push('<p>'+inl(b.p)+'</p>');
    else if(b.bullets)o.push('<ul>'+b.bullets.map(x=>'<li>'+inl(x)+'</li>').join('')+'</ul>');
    else if(b.numbers)o.push('<ol>'+b.numbers.map(x=>'<li>'+inl(x)+'</li>').join('')+'</ol>');
    else if(b.table){const t=b.table;o.push('<table border="1" cellpadding="4"><tr>'+t.headers.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr>'+t.rows.map(r=>'<tr>'+r.map(c=>'<td>'+String(c).split('\n').map(inl).join('<br>')+'</td>').join('')+'</tr>').join('')+'</table>');}
    else if(b.prompt)o.push('<p><b>Prompt to copy</b></p><p>'+esc(b.prompt)+'</p>');
  }
  o.push('</body></html>');
  return o.join('\n');
}
function build(blocks, title, outPath) {
  if (process.env.HTML_OUT) require('fs').writeFileSync(process.env.HTML_OUT, html(blocks));
  const numbering = [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }];
  let n = 0;
  const children = [];
  for (const b of blocks) {
    if (b.title) children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun({ text: b.title })] }));
    else if (b.sub) children.push(new Paragraph({ spacing: { after: 160 }, children: runs(b.sub, { italics: true, color: '595959' }) }));
    else if (b.h1) children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: b.h1 })] }));
    else if (b.h2) children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: b.h2 })] }));
    else if (b.p) children.push(new Paragraph({ spacing: { after: 120 }, children: runs(b.p) }));
    else if (b.bullets) b.bullets.forEach((t) => children.push(new Paragraph({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 60 }, children: runs(t) })));
    else if (b.numbers) {
      const ref = 'num' + (n++);
      numbering.push({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] });
      b.numbers.forEach((t) => children.push(new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60 }, children: runs(t) })));
    } else if (b.table) { children.push(table(b.table.headers, b.table.rows, b.table.widths)); children.push(new Paragraph({ spacing: { after: 120 }, children: [] })); }
    else if (b.prompt) {
      children.push(new Paragraph({ spacing: { before: 60, after: 40 }, children: [new TextRun({ text: 'Prompt to copy', bold: true, size: 20, color: '1F4E79' })] }));
      children.push(new Paragraph({
        spacing: { after: 160 }, shading: { fill: 'F2F2F2', type: ShadingType.CLEAR, color: 'auto' },
        border: { left: { style: BorderStyle.SINGLE, size: 18, color: '1F4E79', space: 8 } }, indent: { left: 200 },
        children: [new TextRun({ text: b.prompt, font: 'Consolas', size: 19 })],
      }));
    } else if (b.pagebreak) children.push(new Paragraph({ children: [new d.PageBreak()] }));
  }
  const doc = new Document({
    title,
    styles: {
      default: {
        document: { run: { font: 'Calibri', size: 22 } },
        title: { run: { size: 44, bold: true, color: '1F4E79', font: 'Calibri' }, paragraph: { spacing: { after: 80 } } },
        heading1: { run: { size: 30, bold: true, color: '1F4E79', font: 'Calibri' }, paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 0 } },
        heading2: { run: { size: 25, bold: true, color: '2E2E2E', font: 'Calibri' }, paragraph: { spacing: { before: 220, after: 80 }, outlineLevel: 1 } },
      },
    },
    numbering: { config: numbering },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: title + '  |  Page ', size: 18, color: '7F7F7F' }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '7F7F7F' })] })] }) },
      children,
    }],
  });
  return Packer.toBuffer(doc).then((buf) => require('fs').writeFileSync(outPath, buf));
}

module.exports = { build };
