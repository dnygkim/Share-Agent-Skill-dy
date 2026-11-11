# deck_lib.pl — 덱 HTML · 콘텐츠 초안(md)을 장표 단위로 읽는 공용 함수
# diff_deck.pl · check_style.pl 이 require 한다. 코어 모듈만 사용(설치 불필요).
use strict; use warnings; use utf8;
use Digest::MD5 qw(md5_hex);

sub dl_read {
  my ($path) = @_;
  open(my $fh, '<:raw', $path) or die "파일을 열 수 없음: $path ($!)\n";
  local $/; my $s = <$fh>; close $fh;
  utf8::decode($s);
  $s =~ s/^\x{FEFF}//;
  return $s;
}

sub dl_unesc {
  my ($t) = @_;
  $t =~ s/&lt;/</g; $t =~ s/&gt;/>/g; $t =~ s/&quot;/"/g; $t =~ s/&#39;/'/g;
  $t =~ s/&nbsp;/ /g; $t =~ s/&middot;/·/g; $t =~ s/&rarr;/→/g; $t =~ s/&amp;/&/g;
  return $t;
}

# 태그를 걷어낸 한 줄 텍스트
sub dl_inline {
  my ($h) = @_;
  return '' unless defined $h;
  $h =~ s/<br\s*\/?>/ /g; $h =~ s/<[^>]+>//g; $h = dl_unesc($h);
  $h =~ s/[\s\x{a0}]+/ /g; $h =~ s/^ | $//g;
  return $h;
}

# 블록 경계를 줄바꿈으로 바꿔 줄 목록으로
sub dl_lines {
  my ($h) = @_;
  # 붙어 있는 인라인 요소(라벨 + 내용)는 한 칸 띄워 읽는다
  $h =~ s{(</(?:span|b|i|em|strong|small|u)>)(?=<(?:span|b|i|em|strong|small|u)\b)}{$1 }g;
  $h =~ s/<(?:br|\/p|\/div|\/li|\/h\d|\/tr|\/td|\/th|\/dt|\/dd)\b[^>]*>/\n/g;
  $h =~ s/<[^>]+>//g; $h = dl_unesc($h);
  my @l;
  for my $x (split /\n/, $h) {
    $x =~ s/[ \t\x{a0}]+/ /g; $x =~ s/^ | $//g;
    push @l, $x if length $x;
  }
  return @l;
}

# 덱 HTML → 장표 목록
sub dl_slides_html {
  my ($s) = @_;
  $s =~ s/^.*?(?=<body\b)//s;
  my @parts = grep { /^<section\b/ } split /(?=<section\b)/, $s;
  my @out; my $n = 0;
  for my $p (@parts) {
    my ($head) = $p =~ /^(<section[^>]*>)/;
    my ($cls)  = $head =~ /class="([^"]*)"/;  $cls //= '';
    next if @parts > 1 && $cls !~ /\bslide\b/ && grep { /^<section[^>]*class="[^"]*\bslide\b/ } @parts;
    $n++;
    my %sl = (idx => $n, class => $cls);
    ($sl{code}) = $head =~ /data-code="([^"]*)"/;
    ($sl{part}) = $head =~ /data-part="([^"]*)"/;
    ($sl{chap}) = $head =~ /data-chap="([^"]*)"/;

    my $w = $p;
    $w =~ s/<!--.*?-->//gs;
    $w =~ s/="data:[^"]*"/=""/g;
    # 시각 서명: 쪽 번호 · 저작권 푸터를 뺀 원문 해시(이미지 · 벡터 · 스타일 변화 감지)
    my $sig = $p;
    $sig =~ s/<div class="dfoot">.*?<\/div>//gs;
    $sig =~ s/<span class="pg[^"]*"[^>]*>\s*\d+\s*<\/span>//g;
    $sig =~ s/&lt;b&gt;\d{1,3}&lt;\/b&gt;//g;
    $sig =~ s/\s+/ /g;
    { my $b = $sig; utf8::encode($b); $sl{sig} = md5_hex($b); }

    my ($crumb) = $w =~ /<div class="crumb">(.*?)<\/div>/s;
    if (defined $crumb) {
      my ($a) = $crumb =~ /<b>(.*?)<\/b>/s;
      my ($b) = $crumb =~ /<span>(.*?)<\/span>/s;
      $sl{chapter} = dl_inline($a); $sl{section} = dl_inline($b);
    }
    if (!defined $sl{code} || $sl{code} eq '') {
      my ($c) = $w =~ /<div class="code">([^<]*)<\/div>/;
      $sl{code} = defined $c ? dl_inline($c) : '';
    }
    my ($tag) = $w =~ /<div class="tagline">(.*?)<\/div>/s;
    my ($ttl) = $w =~ /<div class="bigtitle">(.*?)<\/div>/s;
    ($ttl) = $w =~ /<h1[^>]*class="[^"]*slide-title[^"]*"[^>]*>(.*?)<\/h1>/s unless defined $ttl;
    ($ttl) = $w =~ /<h[12][^>]*>(.*?)<\/h[12]>/s unless defined $ttl;
    $sl{tagline} = dl_inline($tag); $sl{title} = dl_inline($ttl);
    $sl{title_sentences} = defined $ttl ? scalar(() = dl_inline($ttl) =~ /(?:니다|[가-힣])[.?!](?=\s|$)/g) : 0;

    my $b = $w;
    $b =~ s/<div class="dfoot">.*?<\/div>//gs;
    $b =~ s/<div class="ptop">.*?<\/div>\s*<\/div>\s*<\/div>//s;         # crumb + lockup
    $b =~ s/<div class="crumb">.*?<\/div>//gs;
    $b =~ s/<div class="lockup">.*?<\/div>//gs;
    $b =~ s/<div class="codebox[^"]*">(?:\s*<div[^>]*>[^<]*<\/div>)*\s*<\/div>//gs;
    $b =~ s/<span class="pg[^"]*"[^>]*>.*?<\/span>//gs;
    $b =~ s/<div class="tagline">.*?<\/div>//s;
    $b =~ s/<div class="bigtitle">.*?<\/div>//s;
    $b =~ s/<(style|script|svg)\b.*?<\/\1>/ /gs;
    $b =~ s/srcdoc="([^"]*)"/' '.dl_unesc($1)/ge;
    $b =~ s/<(style|script|svg)\b.*?<\/\1>/ /gs;
    $b =~ s/^<section[^>]*>//;
    my @l = grep { $_ ne '×' && !/^©/ } dl_lines($b);
    $sl{lines} = \@l;
    $sl{kind} = $cls =~ /\bs-emb\b/ ? '발표용 iframe' : $cls =~ /\bs-fig\b/ ? '피그마 벡터'
              : $cls =~ /\b(?:cover|cvfull|dv)\b/ ? '표지 · 간지' : '일반';
    $sl{label} = ($sl{code} ne '' ? $sl{code} : "p$n");
    push @out, \%sl;
  }
  return @out;
}

# 콘텐츠 초안(04_content.md) → 장표 목록
# 장표 블록 = 「### [코드] 태그라인」 머리 + 「- 거버닝: …」 줄 (agents/slide-builder.md 서식)
sub dl_slides_md {
  my ($s) = @_;
  my @out; my $cur; my $n = 0; my $chapter = '';
  for my $line (split /\r?\n/, $s) {
    if ($line =~ /^##\s+(.+)/ && $line !~ /^###/) { $chapter = $1; next; }
    if ($line =~ /^###\s+(.+)/) {
      my $h = $1; $n++;
      my ($code) = $h =~ /^\[([^\]]+)\]/; $h =~ s/^\[[^\]]+\]\s*//;
      $cur = { idx => $n, code => $code // '', chapter => $chapter, section => '', tagline => $h,
               title => '', title_sentences => 0, lines => [], kind => '초안', class => '', sig => '' };
      $cur->{label} = $cur->{code} ne '' ? $cur->{code} : "p$n";
      push @out, $cur; next;
    }
    next unless $cur;
    my $t = $line;
    $t =~ s/^\s*(?:[-*+]|\d+\.)\s+//; $t =~ s/^\s*>\s*//; $t =~ s/\*\*|__|`//g; $t =~ s/^\s+|\s+$//g;
    next if $t eq '' || $t =~ /^\|?[\s:|-]+\|?$/;
    if ($t =~ /^거버닝(?:\s*메시지)?\s*[:：]\s*(.+)/) {
      $cur->{title} = $1;
      $cur->{title_sentences} = scalar(() = $1 =~ /(?:니다|[가-힣])[.?!](?=\s|$)/g);
      next;
    }
    next if $t =~ /^(?:레이아웃|패턴|근거|출처|레퍼런스|비고|자기검증)\s*[:：]/;   # 작업 메모 줄은 문체 점검 제외
    if ($t =~ /\|/) { push @{$cur->{lines}}, grep { length } map { s/^\s+|\s+$//gr } split /\|/, $t; }
    else { push @{$cur->{lines}}, $t; }
  }
  return @out;
}

sub dl_slides {
  my ($path) = @_;
  my $s = dl_read($path);
  return $path =~ /\.md$/i ? dl_slides_md($s) : dl_slides_html($s);
}

1;
