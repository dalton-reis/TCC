# Biblioteca da FURB

O portal utiliza uma sessão PHP para manter o cabeçalho de autoridade
selecionado. Por isso, uma URL com `CdCabecalho` pode retornar zero obras quando
aberta sem antes inicializar a sessão na página de busca.

Fluxo implementado:

1. abrir `pesqCabecalho.php?menu=rapida` para inicializar a sessão;
2. abrir o cabeçalho configurado em `biblioteca.authority_url`;
3. coletar todas as páginas `consultaCabecalho.php?...&pagina=N`;
4. abrir cada detalhe `recuperaMfnCompleto.php?...&CdMFN=N`;
5. salvar o HTML bruto e extrair os campos.

O cabeçalho `CdCabecalho=67983` possui 164 títulos na consulta observada. Nem
todo título é necessariamente TCC; a revisão do CSV continua obrigatória.
