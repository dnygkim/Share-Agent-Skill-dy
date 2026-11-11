#!/usr/bin/env perl
# diff_deck.pl — 직전 추출본 대비 변경분을 장표 단위로 뽑는다 (2차 추출부터 사용)
#
# 사용법:
#   perl scripts/diff_deck.pl <직전본.html> <신규본.html> [--md 변경분.md] [--json 변경분.json] [--max 8]
#
# 하는 일: 두 덱의 장표를 코드(data-code · 코드박스)로 짝짓고, 코드가 바뀐 장표는 제목 · 본문 유사도로 다시 짝짓는다.
#   변경 유형 = 신규 / 삭제 / 헤드라인 / 태그라인 / 본문 / 시각(문구는 같고 이미지 · 벡터 · 스타일만 변경) / 이동 / 코드 변경 / 동일
#   쪽 번호 · 저작권 푸터의 변화는 변경으로 세지 않는다.
# 산출: 목차(장 > 절) 순서의 마크다운 + (선택) JSON. 변경분 HTML 간략본은 이 데이터를 근거로 만든다(agents/feedback-integrator.md).
# 의존성: perl 5 코어 모듈만. Git Bash(Windows) · macOS 기본 perl 에서 그대로 실행.
use strict; use warnings; use utf8;
use FindBin qw($Bin);
require "$Bin/deck_lib.pl";
binmode(STDOUT, ':utf8'); binmode(STDERR, ':utf8');

my (@files, $md, $json); my $max = 8;
while (@ARGV) {
  my $a = shift @ARGV;
  if    ($a eq '--md')   { $md   = shift @ARGV }
  elsif ($a eq '--json') { $json = shift @ARGV }
  elsif ($a eq '--max')  { $max  = shift @ARGV }
  else                   { push @files, $a }
}
if (@files != 2) { print "사용법: perl scripts/diff_deck.pl <직전본.html> <신규본.html> [--md out.md] [--json out.json] [--max 8]\n"; exit 2; }

my @old = dl_slides($files[0]);
my @new = dl_slides($files[1]);
die "직전본에서 장표(section)를 찾지 못함\n" unless @old;
die "신규본에서 장표(section)를 찾지 못함\n" unless @new;

sub name_of { my $p = shift; $p =~ s{.*[/\\]}{}; utf8::decode($p); return $p; }

# ── 1) 짝짓기 ───────────────────────────────────────────────
my (%pair, %used);        # new idx -> old idx
my (%oc, %nc);
$oc{$_->{code}}++ for grep { $_->{code} ne '' } @old;
$nc{$_->{code}}++ for grep { $_->{code} ne '' } @new;
my %obycode = map { $_->{code} => $_ } grep { $_->{code} ne '' && $oc{$_->{code}} == 1 } @old;
for my $n (@new) {
  my $c = $n->{code};
  next unless $c ne '' && $nc{$c} == 1 && $obycode{$c};
  $pair{$n->{idx}} = $obycode{$c}{idx}; $used{$obycode{$c}{idx}} = 1;
}
sub sim {
  my ($a, $b) = @_;
  return 1 if $a->{sig} eq $b->{sig};
  my %s; $s{$_} |= 1 for @{$a->{lines}}, ($a->{title} // ''); $s{$_} |= 2 for @{$b->{lines}}, ($b->{title} // '');
  delete $s{''};
  my $all = keys %s or return 0;
  my $both = grep { $s{$_} == 3 } keys %s;
  my $j = $both / $all;
  $j = 0.6 if $j < 0.6 && $a->{title} ne '' && $a->{title} eq $b->{title};
  return $j;
}
my @cand;
for my $n (grep { !exists $pair{$_->{idx}} } @new) {
  for my $o (grep { !$used{$_->{idx}} } @old) {
    my $s = sim($o, $n);
    push @cand, [$s, $n->{idx}, $o->{idx}] if $s >= 0.5;
  }
}
for my $c (sort { $b->[0] <=> $a->[0] } @cand) {
  next if exists $pair{$c->[1]} || $used{$c->[2]};
  $pair{$c->[1]} = $c->[2]; $used{$c->[2]} = 1;
}

# ── 2) 이동 판정: 짝지어진 장표의 직전본 순서가 늘어나는 최장 부분열에서 빠진 장표 ──
my @seq = map { [$_->{idx}, $pair{$_->{idx}}] } grep { exists $pair{$_->{idx}} } @new;
my (@len, @prev); my ($best, $bi) = (0, -1);
for my $i (0 .. $#seq) {
  $len[$i] = 1; $prev[$i] = -1;
  for my $k (0 .. $i - 1) {
    if ($seq[$k][1] < $seq[$i][1] && $len[$k] + 1 > $len[$i]) { $len[$i] = $len[$k] + 1; $prev[$i] = $k; }
  }
  ($best, $bi) = ($len[$i], $i) if $len[$i] > $best;
}
my %keep; for (my $i = $bi; $i >= 0; $i = $prev[$i]) { $keep{$seq[$i][0]} = 1; }

# ── 3) 장표별 비교 ─────────────────────────────────────────
my %oidx = map { $_->{idx} => $_ } @old;
my (@rows, %cnt);
sub mdiff {
  my ($a, $b) = @_;
  my %c; $c{$_}++ for @$a; my @add;
  for my $x (@$b) { if ($c{$x}) { $c{$x}-- } else { push @add, $x } }
  my %d; $d{$_}++ for @$b; my @del;
  for my $x (@$a) { if ($d{$x}) { $d{$x}-- } else { push @del, $x } }
  return (\@del, \@add);
}
for my $n (@new) {
  my %r = (new => $n, types => []);
  if (!exists $pair{$n->{idx}}) { push @{$r{types}}, '신규'; }
  else {
    my $o = $oidx{$pair{$n->{idx}}}; $r{old} = $o;
    push @{$r{types}}, '코드 변경' if $o->{code} ne $n->{code};
    push @{$r{types}}, '이동'      if !$keep{$n->{idx}};
    push @{$r{types}}, '절 변경'   if ($o->{section} // '') ne ($n->{section} // '') || ($o->{chapter} // '') ne ($n->{chapter} // '');
    push @{$r{types}}, '헤드라인'  if $o->{title} ne $n->{title};
    push @{$r{types}}, '태그라인'  if $o->{tagline} ne $n->{tagline};
    my ($del, $add) = mdiff($o->{lines}, $n->{lines});
    if (@$del || @$add) { push @{$r{types}}, '본문'; $r{del} = $del; $r{add} = $add; }
    elsif (join("\n", @{$o->{lines}}) ne join("\n", @{$n->{lines}})) { push @{$r{types}}, '본문 순서'; }
    # 문구가 전부 같은데 원문 해시가 다르면 이미지 · 벡터 · 스타일만 바뀐 장표
    push @{$r{types}}, '시각' if $o->{sig} ne $n->{sig} && !grep { /^(?:헤드라인|태그라인|본문|본문 순서)$/ } @{$r{types}};
    push @{$r{types}}, '동일' unless @{$r{types}};
  }
  $cnt{$_}++ for @{$r{types}};
  push @rows, \%r;
}
my @gone = grep { !$used{$_->{idx}} } @old;
$cnt{'삭제'} = scalar @gone;
my $changed = grep { !($_->{types}[0] eq '동일') } @rows;

# ── 4) 마크다운 ────────────────────────────────────────────
sub cell { my $t = shift // ''; $t =~ s/\|/／/g; return $t; }
sub clip { my $t = shift; return length($t) > 90 ? substr($t, 0, 88) . '…' : $t; }
my $out = '';
$out .= "# 변경분 데이터\n\n";
$out .= "- 직전본: `" . name_of($files[0]) . "` · " . scalar(@old) . "장\n";
$out .= "- 신규본: `" . name_of($files[1]) . "` · " . scalar(@new) . "장\n";
$out .= "- 변경 장표 " . ($changed + @gone) . "장 (신규본 기준 변경 $changed · 삭제 " . scalar(@gone) . ")\n";
$out .= "- 유형별: " . join(' · ', map { "$_ " . ($cnt{$_} // 0) } ('신규', '삭제', '헤드라인', '태그라인', '본문', '본문 순서', '시각', '이동', '코드 변경', '절 변경', '동일')) . "\n";
$out .= "- 읽는 법: 「시각」 = 문구는 같고 이미지 · 벡터 · 스타일만 달라진 장표(렌더 PNG 로 확인) · 「이동」 = 앞뒤 순서가 바뀐 장표 · 쪽 번호 변화는 세지 않음\n\n";
$out .= "## 목차별 변경\n\n";
# 크럼이 없는 장표(표지 · 간지 · 맺음)의 소속 장: 첫 장 앞 = 「표지 · 목차」, 간지 = 뒤따르는 장, 그 밖 = 앞 장
my %group; my $prevch = '';
for my $i (0 .. $#new) {
  my $n = $new[$i];
  if (($n->{chapter} // '') ne '') { $group{$n->{idx}} = $prevch = $n->{chapter}; next; }
  my ($next) = grep { ($_->{chapter} // '') ne '' } @new[$i + 1 .. $#new];
  my $isdv = $n->{class} =~ /\b(?:dv|cover)\b/ && $next && ($n->{part} // '') eq ($next->{part} // '');
  $group{$n->{idx}} = $prevch eq '' && !($isdv && $i > 1) ? '표지 · 목차' : $isdv ? $next->{chapter} : $prevch;
}
my $curch = "\0";
for my $r (@rows) {
  my $n = $r->{new};
  my $ch = $group{$n->{idx}};
  if ($ch ne $curch) {
    $out .= "\n### $ch\n\n| 쪽(직전→신규) | 코드 | 절 · 태그라인 | 변경 유형 | 헤드라인(신규본) |\n|---|---|---|---|---|\n";
    $curch = $ch;
  }
  my $pg = ($r->{old} ? $r->{old}{idx} : '—') . '→' . $n->{idx};
  my $code = $n->{code}; $code = "$r->{old}{code}→$code" if $r->{old} && $r->{old}{code} ne $n->{code};
  my $sec = $n->{tagline} ne '' ? $n->{tagline} : ($n->{section} // '');
  $sec = $n->{kind} if $sec eq '';
  $out .= '| ' . join(' | ', $pg, cell($code), cell($sec), join(' · ', @{$r->{types}}), cell($n->{title})) . " |\n";
}
$out .= "\n## 장표별 상세\n";
for my $r (grep { $_->{types}[0] ne '동일' } @rows) {
  my $n = $r->{new}; my $o = $r->{old};
  $out .= "\n### $n->{label} · " . ($n->{tagline} ne '' ? $n->{tagline} : $n->{kind}) . ' (쪽 ' . ($o ? $o->{idx} : '—') . "→$n->{idx}) · " . join(' · ', @{$r->{types}}) . "\n";
  if (!$o) {
    $out .= "- 헤드라인: 「$n->{title}」\n" if $n->{title} ne '';
    my @l = @{$n->{lines}}; my $more = @l > $max ? @l - $max : 0; splice(@l, $max) if $more;
    $out .= "- 본문 발췌: " . join(' / ', map { clip($_) } @l) . ($more ? " … 외 ${more}줄" : '') . "\n" if @l;
    next;
  }
  $out .= "- 헤드라인: 「$o->{title}」 → 「$n->{title}」\n" if $o->{title} ne $n->{title};
  $out .= "- 태그라인: 「$o->{tagline}」 → 「$n->{tagline}」\n" if $o->{tagline} ne $n->{tagline};
  $out .= "- 절: 「" . ($o->{section} // '') . "」 → 「" . ($n->{section} // '') . "」\n" if grep { $_ eq '절 변경' } @{$r->{types}};
  for my $k (['del', '삭제 문구'], ['add', '추가 문구']) {
    my $l = $r->{$k->[0]} or next; next unless @$l;
    my @l = @$l; my $more = @l > $max ? @l - $max : 0; splice(@l, $max) if $more;
    $out .= "- $k->[1] (" . scalar(@$l) . "줄)\n" . join('', map { "  - " . clip($_) . "\n" } @l) . ($more ? "  - … 외 ${more}줄\n" : '');
  }
  $out .= "- 문구 동일 · 줄 순서만 변경\n" if grep { $_ eq '본문 순서' } @{$r->{types}};
  $out .= "- 문구 동일 · 이미지/벡터/스타일 변경 → 렌더 PNG 비교 필요\n" if grep { $_ eq '시각' } @{$r->{types}};
}
if (@gone) {
  $out .= "\n## 삭제된 장표\n\n| 직전 쪽 | 코드 | 절 · 태그라인 | 헤드라인(직전본) |\n|---|---|---|---|\n";
  $out .= '| ' . join(' | ', $_->{idx}, cell($_->{code}), cell($_->{tagline} ne '' ? $_->{tagline} : ($_->{section} // $_->{kind})), cell($_->{title})) . " |\n" for @gone;
}

if ($md) { open(my $fh, '>:utf8', $md) or die "$md: $!\n"; print $fh $out; close $fh; print "저장: " . name_of($md) . "\n"; }
else { print $out; }

if ($json) {
  require JSON::PP;
  my $slim = sub { my $s = shift or return undef; return { page => $s->{idx}, code => $s->{code}, chapter => $s->{chapter}, section => $s->{section}, tagline => $s->{tagline}, title => $s->{title}, kind => $s->{kind} } };
  my $data = {
    old_file => name_of($files[0]), new_file => name_of($files[1]),
    old_count => scalar(@old), new_count => scalar(@new), counts => \%cnt,
    slides => [ map { { new => $slim->($_->{new}), old => $slim->($_->{old}), types => $_->{types}, deleted_lines => $_->{del} // [], added_lines => $_->{add} // [] } } @rows ],
    deleted => [ map { $slim->($_) } @gone ],
  };
  open(my $fh, '>:raw', $json) or die "$json: $!\n";
  print $fh JSON::PP->new->utf8->pretty->canonical->encode($data); close $fh;
  print "저장: " . name_of($json) . "\n";
}
print STDERR "변경 " . ($changed + @gone) . "장 / 신규본 " . scalar(@new) . "장\n";
exit 0;
