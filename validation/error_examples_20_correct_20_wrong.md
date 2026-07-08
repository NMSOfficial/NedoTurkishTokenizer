# Error Examples: 20 Correct / 20 Wrong

## Correct examples

| word | gold | pred | origin |
|---|---|---|---|
| öğretmenlerimizin | `öğretmen+ler+imiz+in` | `öğretmen+ler+imiz+in` | annotator_agreed |
| öğrencilerimizin | `öğrenci+ler+imiz+in` | `öğrenci+ler+imiz+in` | annotator_agreed |
| görüşmelerimizi | `görüşme+ler+imiz+i` | `görüşme+ler+imiz+i` | annotator_agreed |
| kademelerimizde | `kademe+ler+imiz+de` | `kademe+ler+imiz+de` | annotator_agreed |
| Üreticilerimize | `Üretici+ler+imiz+e` | `Üretici+ler+imiz+e` | annotator_agreed |
| kurulabilirler | `kurul+abil+ir+ler` | `kurul+abil+ir+ler` | annotator_agreed |
| buluşmalarını | `buluşma+lar+ı+nı` | `buluşma+lar+ı+nı` | annotator_agreed |
| derslerimizin | `ders+ler+imiz+in` | `ders+ler+imiz+in` | annotator_agreed |
| programlarına | `program+lar+ın+a` | `program+lar+ın+a` | annotator_agreed |
| yaklaşmasının | `yaklaş+ma+sı+nın` | `yaklaş+ma+sı+nın` | annotator_agreed |
| yapılabilmesi | `yapıl+abil+me+si` | `yapıl+abil+me+si` | annotator_agreed |
| askerlerinin | `asker+ler+i+nin` | `asker+ler+i+nin` | annotator_agreed |
| başrollerini | `başrol+ler+i+ni` | `başrol+ler+i+ni` | annotator_agreed |
| bölgelerinde | `bölge+ler+in+de` | `bölge+ler+in+de` | annotator_agreed |
| değerlerdeki | `değer+ler+de+ki` | `değer+ler+de+ki` | annotator_agreed |
| görüşmesinin | `görüş+me+si+nin` | `görüş+me+si+nin` | annotator_agreed |
| raporlarının | `rapor+lar+ı+nın` | `rapor+lar+ı+nın` | annotator_agreed |
| sorunlarının | `sorun+lar+ı+nın` | `sorun+lar+ı+nın` | annotator_agreed |
| velilerimize | `veli+ler+imiz+e` | `veli+ler+imiz+e` | annotator_agreed |
| deneyemedim | `deney+e+me+dim` | `deney+e+me+dim` | annotator_agreed |

## Wrong examples

| word | gold | pred | fp | fn | mode |
|---|---|---|---:|---:|---|
| yakalayacağını | `yakala+yacağ+ı+nı` | `yakalay+a+ca+ğı+nı` | 3 | 2 | over+under |
| teşkilatında | `teşkilat+ı+nda` | `teşkil+a+tın+da` | 3 | 2 | over+under |
| kullanılan | `kullan+ıl+an` | `kul+la+nı+lan` | 3 | 2 | over+under |
| şirketinin | `şirket+i+nin` | `şirk+e+tin+in` | 3 | 2 | over+under |
| gençleştirmesinde | `genç+leş+tir+me+si+nde` | `gençleştir+me+sin+de` | 1 | 3 | over+under |
| GERÇEKLEŞTİRDİK | `GERÇEK+LEŞ+TİR+Dİ+K` | `GERÇEKLEŞTİRDİK` | 0 | 4 | under |
| belirtilerinin | `belirti+ler+i+nin` | `belirtil+e+ri+nin` | 2 | 2 | over+under |
| ilgilenmeyince | `ilgilen+me+yince` | `ilgilenmey+in+ce` | 2 | 2 | over+under |
| katılamazlar | `katıl+a+ma+z+lar` | `katılamazlar` | 0 | 4 | under |
| kıyılarında | `kıyı+lar+ı+nda` | `kıyıl+ar+ın+da` | 2 | 2 | over+under |
| mağduriyeti | `mağduriyet+i` | `mağdur+i+ye+ti` | 3 | 1 | over+under |
| unutmayınız | `unut+ma+yınız` | `unutmay+ın+ız` | 2 | 2 | over+under |
| yatırdığını | `yatır+dığ+ı+nı` | `yatırd+ı+ğı+nı` | 2 | 2 | over+under |
| ödemesine | `öde+me+si+ne` | `ödem+e+sin+e` | 2 | 2 | over+under |
| Kariyeri | `Kariyer+i` | `Kar+i+ye+ri` | 3 | 1 | over+under |
| uğradığı | `uğra+dığ+ı` | `uğrad+ı+ğı` | 2 | 2 | over+under |
| altında | `alt+ı+nda` | `al+tın+da` | 2 | 2 | over+under |
| derdine | `derd+i+ne` | `der+din+e` | 2 | 2 | over+under |
| tadını | `tad+ı+nı` | `ta+dın+ı` | 2 | 2 | over+under |
| KIRIŞIKLIKLARINI | `KIRIŞIKLIK+LAR+I+NI` | `KIRIŞIKLIKLARINI` | 0 | 3 | under |