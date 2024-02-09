# Add-Mac-to-ISE

<center>
![](https://community.cisco.com/t5/image/serverpage/image-id/88717i58C1026086094BD0?v=v2)
</center>

## Funcionalidade
### Adiciona MACs automático em um Identity Group no ISE
### Ele pede a descrição do grupo, caso o grupo já exista ele não altera a descrição, apenas adiciona os MACs no grupo já existente, além de conseguir criar um grupo e adicionar os MACs automáticos

## Ressalva:
### É necessário habilitar o ESR Admin acessando System / Settings / API Settings / API Service Settings / Habilite em API Service Settings for Primary Administration Node a opção ESR (Read/Write)
### É recomendado criar um usuário com a permissão ESR Admin para consumir a API do ISE, mas um usuário com permissão Super Admin poderia ser usado também
### O arquivo passado precisa ser um .txt e os MACs precisam estar um em cada linha, não é necessário estar formatado (o script formata o MAC)
