# Relatório de Aging

https://agingtrescon-zz8b4cvjsgwrgbxhzdsgpf.streamlit.app/

. Abrindo o sistema
Acesse o aplicativo Streamlit no navegador, utilizando o link disponibilizado (ex: via GitHub Pages ou Streamlit Cloud).
Relatório de Aging - Conciliador · Streamlit
________________________________________
## 2. Importando os dados de TÍTULOS
1.	Vá até a seção "1️⃣ Importar Títulos" no menu lateral.
2.	Clique em Selecionar Arquivo e escolha um arquivo .xlsx.
3.	Selecione a aba da planilha contendo os títulos a receber.
4.	Os dados serão carregados e aparecerão os primeiros registros.
________________________________________
## 3. Extraindo os campos dos TÍTULOS
1.	Acesse a seção "2️⃣ Extrair Títulos".
2.	Para cada campo lógico (Fornecedor, Número do Título, Emissão, Vencimento, Valor), selecione a coluna correspondente.
3.	Mantenha marcada a opção "Ajustar?" para usar regex inteligente (recomendado).
4.	Ao final, o sistema irá exibir os dados tratados.
5.	Verifique se os dados estão corretos.
6.	Clique em "Próximo" (ou vá manualmente para o próximo passo no menu).
________________________________________
## 4. Importando os dados de BAIXAS
1.	Vá para "3️⃣ Importar Baixas".
2.	Novamente, selecione um arquivo .xlsx e escolha a aba desejada.
3.	Confirme a visualização inicial dos dados.
________________________________________
## 5. Extraindo os campos das BAIXAS
1.	Acesse "4️⃣ Extrair Baixas".
2.	Mapeie os campos da mesma forma que nos títulos:
o	Fornecedor/Cliente
o	Número do Título
o	Data de Pagamento
o	Valor Pago
o	(Opcional: Conta, Documento)
3.	O sistema aplicará expressões regulares e mostrará os dados extraídos.
4.	Os valores vazios serão preenchidos com o conteúdo original da célula.
________________________________________
## 6. Realizando a CONCILIAÇÃO
1.	Acesse "5️⃣ Conciliação".
2.	O sistema vai unificar os dados dos títulos e das baixas.
3.	Será feita uma normalização automática dos nomes dos fornecedores (fuzzy match + limpeza textual).
4.	O sistema irá cruzar por número de documento e classificar cada item:
o	✅ OK
o	⚠️ Pagamento não encontrado
o	⚠️ Título não encontrado
5.	A tabela final será exibida com todos os dados analíticos.
6.	Você poderá baixar o relatório Excel com um botão de download.
________________________________________
## 7. Exportando o relatório final
1.	No final da tela de conciliação, clique em 📥 Baixar Relatório em Excel.
2.	O arquivo virá com todos os campos úteis, incluindo:
o	Fornecedores Originais, Ajustados e Considerados
o	Número de Documento (Título e Baixa)
o	Datas (Emissão, Vencimento, Pagamento)
o	Valor Nominal
o	Status da Conciliação

