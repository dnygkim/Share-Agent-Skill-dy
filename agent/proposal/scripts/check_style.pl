#!/usr/bin/env perl
# check_style.pl — 제안서 문체 점검 (기준 = references/writing-style.md)
#
# 사용법:
#   perl scripts/check_style.pl <덱.html | 04_content.md> [--quiet]
#
# [위반] 종료코드 1 — 추출 전에 0건으로 만든다
#   · ㅁ 명사화 어미(~함 · ~임 · ~음 · ~됨 · ~않음 · ~어짐 · ~따름)로 끝나는 줄 · 절
#   · 호칭(당사 · 저희 · 귀사 · 폐사) · 본문 대시(—) · 이모지
# [주의] 종료코드에 영향 없음 — 한 건씩 읽고 고칠지 판단
#   · AI 상투어 · 근거 없는 형용사 · 번역투 연결어
#   · 거버닝 메시지 40자 초과 · 2문장 · 누락, 한 장에 합니다체 문장 과다
#   · (2026-11-13 최종본 학습 · references/slide-quality-bar.md §4) 거버닝의 「통한/통해」 · 「~으로」 미완결 ·
#     장끼리 같은 거버닝 · 최상급/절대어 · 우리는/여러분 · 띄어쓰기(제한 된 · 강화 합니다) · 「A가 아닌 B」 덱 4회 이상
# 의존성: perl 5 코어 모듈만. Git Bash(Windows) · macOS 기본 perl 에서 그대로 실행.
use strict; use warnings; use utf8;
use FindBin qw($Bin);
require "$Bin/deck_lib.pl";
binmode(STDOUT, ':utf8'); binmode(STDERR, ':utf8');

my ($file, $quiet);
for (@ARGV) { if ($_ eq '--quiet') { $quiet = 1 } else { $file = $_ } }
if (!$file) { print "사용법: perl scripts/check_style.pl <덱.html | 04_content.md> [--quiet]\n"; exit 2; }
my @slides = dl_slides($file);
die "장표를 찾지 못함 (HTML 은 <section class=\"slide\">, md 는 「### [코드] 태그라인」 블록)\n" unless @slides;

# ── 규칙 ──────────────────────────────────────────────────
# 명사로 굳은 말(위반 아님)
my $NOUN_HAM = qr/(?:포함|보관함|수신함|발신함|우편함|사서함|편지함|명함|건의함|투표함|보석함)$/;
my $NOUN_IM  = qr/(?:책임|위임|게임|모임|타임|프레임|선임|담임|연임|해임|부임|취임|퇴임|신임|전임|겸임|일임|방임|재임|역임|중임|초임|라임|패러다임|클레임|^임)$/;
my $NOUN_JIM = qr/(?:다짐|봇짐|등짐|이삿짐|^짐)$/;
my $VERB_EUM = qr/(?:있|없|않|같|많|적|높|낮|좋|싫|받|맞|맡|남|놓|쌓|잃|얻|닿|늦|짧|멀|깊|넓|좁|작|았|었|였|했|됐|겠|섰)음$/;
my $VERB_ETC = qr/(?:어남|타남|러남|끝남|나뉨|바뀜|생김|막힘|밀림|걸림|모자람|다름|따름|드묾|둠)$/;

sub bad_ending {
  my ($seg) = @_;
  my $s = $seg;
  $s =~ s/[\s\)\]」』”’"'\*※]+$//;          # 닫는 괄호 · 따옴표
  $s =~ s/\([^()]*\)$//;                     # 끝의 괄호 보충
  $s =~ s/\s+$//;
  my @w = split /\s+/, $s; return 0 unless @w;
  my $t = $w[-1]; $t =~ s/^[^가-힣A-Za-z0-9]+//;
  return 0 unless $t =~ /[가-힣]$/;
  my $multi = @w >= 2;
  return '함'  if $t eq '함' ? $multi : ($t =~ /함$/ && $t !~ $NOUN_HAM);
  return '됨'  if $t =~ /됨$/;
  return '음'  if $t =~ $VERB_EUM && ($multi || $t =~ /(?:있|없|않|았|었|였|했|됐|겠)음$/);
  return '짐'  if $multi && $t =~ /([가-힣])짐$/ && $t !~ $NOUN_JIM && (ord($1) - 0xAC00) % 28 == 0;
  return '임'  if $multi && $t =~ /임$/ && $t !~ $NOUN_IM;
  return 'ㅁ'  if $multi && $t =~ $VERB_ETC;
  return 0;
}

my @HONOR = ('당사', '저희', '귀사', '폐사');
my @CLICHE = (
  # 근거 없는 형용사
  '혁신적', '획기적', '최적의', '최적화된', '차별화된', '선도적', '다양한', '원활한', '효과적인', '체계적인', '지속적인', '종합적인', '전문적인', '탁월한', '완벽',
  # 최상급 · 절대어 (2026-11-13 최종본 학습)
  '업계 최고', '최초', '유일한', '무결점', '원천 차단', '원천 봉쇄', 'Zero',
  # AI · 보도자료 상투어
  '극대화', '시너지', '유기적', '패러다임', '원스톱', '토탈 솔루션', '고도화된', '한층', '궁극적으로', '나아가', '핵심은', '의 여정', '새로운 가치', '가치를 창출', '경쟁력을 강화', '니즈',
  # 번역투 연결어
  '를 통해', '을 통해', '을 통한', '를 통한', '통하여', '뿐만 아니라', '에 있어', '함으로써', '로 인해', '에 대한', '가능하게', '할 수 있도록', '을 제공합니다', '를 제공합니다',
);
my $TITLE_MAX = 40;     # 거버닝 메시지 길이(공백 포함)
my $NIDA_MAX  = 8;      # 한 장의 합니다체 문장 수

# ── 점검 ──────────────────────────────────────────────────
my (@fail, @warn, %cl); my ($nlines, $nnida) = (0, 0);
my (%titles, @anin);    # 장끼리 같은 거버닝 · 「A가 아닌 B」 횟수
for my $sl (@slides) {
  my $where = "$sl->{label} (p$sl->{idx})";
  my @all = grep { length } ($sl->{title}, @{$sl->{lines}});
  my $nida = 0;
  for my $line (@all) {
    $nlines++;
    $nida++ if $line =~ /니다[.!]?$/ || $line =~ /니다[.,]\s/;
    for my $seg (split /(?<=[가-힣])[,.;]\s+|\s·\s|\s\/\s/, $line) {
      my $e = bad_ending($seg) or next;
      push @fail, "[어미 ~$e] $where: $seg";
    }
    for my $h (@HONOR) { push @fail, "[호칭 $h] $where: $line" if index($line, $h) >= 0; }
    push @fail, "[대시 —] $where: $line" if $line =~ /—/;
    push @fail, "[이모지] $where: $line" if $line =~ /[\x{1F300}-\x{1FAFF}]/;
    push @warn, "[인칭] $where: $line" if $line =~ /(?:^|[\s「‘“'"(])우리(?:는|가)\s/ || $line =~ /여러분/;
    push @warn, "[띄어쓰기] $where: $line" if $line =~ /[가-힣](?![야이가게록지고서을를은는도만에로와과])[가-힣]\s(?:된|합니다|됩니다)(?=[\s.,]|$)/;   # 명사 뒤 띄움만 (해야 합니다 · 시간이 됩니다 제외)
    push @anin, $sl->{label} if $line =~ /(?:가|이)\s?아닌|아니라/;
    for my $c (@CLICHE) { if (index($line, $c) >= 0) { $cl{$c}{n}++; push @{$cl{$c}{w}}, $sl->{label}; } }
  }
  $nnida += $nida;
  if ($sl->{kind} eq '일반' || $sl->{kind} eq '초안') {
    my $t = $sl->{title};
    if ($t eq '') { push @warn, "[거버닝 누락] $where" if $sl->{tagline} ne ''; }
    else {
      push @warn, "[거버닝 " . length($t) . "자] $where: $t" if length($t) > $TITLE_MAX;
      push @warn, "[거버닝 2문장] $where: $t" if $t =~ /(?:니다|[가-힣])\.\s+\S/;
      push @warn, "[거버닝 「통한」] $where: $t" if $t =~ /통한|통해/;
      push @warn, "[거버닝 미완결 ~으로] $where: $t" if $t =~ /(?:으로|[가-힣]로)$/ && $t !~ /(?:그대로|바로|새로|서로|따로|주로|별로|날로|홀로)$/;
      push @{$titles{$t}}, $sl->{label};
    }
    push @warn, "[합니다체 ${nida}문장] $where: 리드 · 결론 · 다짐에만 쓰고 항목은 명사구로" if $nida > $NIDA_MAX;
  }
}
for my $t (sort keys %titles) {
  my @w = @{$titles{$t}};
  push @warn, "[거버닝 중복 " . scalar(@w) . "장] " . join(', ', @w) . ": $t" if @w > 1;
}
push @warn, "[「A가 아닌 B」 × " . scalar(@anin) . "] 덱 전체 3회 이하로: " . join(', ', @anin[0 .. ($#anin > 9 ? 9 : $#anin)]) if @anin > 3;
for my $c (sort { $cl{$b}{n} <=> $cl{$a}{n} } keys %cl) {
  my %seen; my @w = grep { !$seen{$_}++ } @{$cl{$c}{w}};
  push @warn, "[상투어 「$c」 × $cl{$c}{n}] " . join(', ', @w[0 .. ($#w > 9 ? 9 : $#w)]) . (@w > 10 ? ' …' : '');
}

my $name = $file; $name =~ s{.*[/\\]}{}; utf8::decode($name);
print "== 문체 점검: $name ==\n";
print "장표 " . scalar(@slides) . " · 문장(줄) $nlines · 합니다체 $nnida (" . ($nlines ? sprintf('%.0f', 100 * $nnida / $nlines) : 0) . "%)\n";
print "\n[위반] " . scalar(@fail) . "건\n"; print "  $_\n" for @fail;
unless ($quiet) { print "\n[주의] " . scalar(@warn) . "건\n"; print "  $_\n" for @warn; }
print "\n" . (@fail ? "결과: 위반 " . scalar(@fail) . "건 → 고친 뒤 다시 점검\n" : "결과: 위반 없음\n");
exit(@fail ? 1 : 0);
